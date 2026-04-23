import os
import json
import base64
from pathlib import Path
from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    project_dir: str
    frames: List[str]
    idx: int
    transcript: List[Dict[str, Any]]
    history: List[str]
    story_plan: List[str]
    fps: float
    prompt: str
    context: str
    frames_since_last_review: int
    is_valid: bool

from openai import OpenAI
from prompts import AGENT_PLANNING_PROMPT, AGENT_REFLEXIVE_PROMPT

class TechnicalAgent:
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model = model
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
        elif self.provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            api_key = os.getenv("OLLAMA_API_KEY", "ollama")
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            self.client = None

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_story_plan(self, project_dir: str, prompt: str, context: str) -> Dict[str, Any]:
        """
        Samples frames every ~30 seconds to generate a high-level story plan.
        """
        frames_dir = Path(project_dir) / ".unmuted" / "plan_frames"
        all_frames = sorted([f for f in frames_dir.iterdir() if f.is_file() and f.suffix == '.jpg']) if frames_dir.exists() else []

        if not all_frames:
            return {"plan": ["No frames found."]}
        
        # Sample frames roughly evenly, max 10 frames to avoid huge payloads
        num_samples = min(10, len(all_frames))
        step = max(1, len(all_frames) // num_samples)
        sampled_frames = all_frames[::step][:num_samples]
        
        if (os.getenv("OPENAI_API_KEY") is None and self.provider == "openai") or self.provider == "mock":
            return {"plan": ["[MOCK PLAN] 1. Opening the application.", "[MOCK PLAN] 2. Navigating the UI.", "[MOCK PLAN] 3. Completing the task."]}

        messages = [
            {"role": "system", "content": AGENT_PLANNING_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": f"Video Intent: {prompt}\nTechnical Context: {context}\nAnalyze these keyframes to produce a Story Plan."}
            ]}
        ]
        
        for i, frame_path in enumerate(sampled_frames):
            b64_img = self._encode_image(str(frame_path))
            messages[1]["content"].append({"type": "text", "text": f"Keyframe {i+1}:"})
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_img}", "detail": "low"}
            })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={ "type": "json_object" },
                max_tokens=800,
                temperature=0.4
            )
            data = json.loads(response.choices[0].message.content)
            return data
        except Exception as e:
            print(f"Error generating story plan: {e}")
            return {"plan": ["Error generating plan."]}


    def reflexive_review(self, recent_transcript: List[Dict[str, Any]], story_plan: List[str]) -> Dict[str, Any]:
        """
        Reviews recent narration history against the Story Plan to detect drift.
        """
        if (os.getenv("OPENAI_API_KEY") is None and self.provider == "openai") or self.provider == "mock":
            return {"valid": True, "reasoning": "[MOCK] Looks good"}

        messages = [
            {"role": "system", "content": AGENT_REFLEXIVE_PROMPT},
            {"role": "user", "content": json.dumps({
                "story_plan": story_plan,
                "recent_transcript": recent_transcript
            }, indent=2)}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={ "type": "json_object" },
                max_tokens=400,
                temperature=0.1
            )
            data = json.loads(response.choices[0].message.content)
            return data
        except Exception as e:
            print(f"Error in reflexive review: {e}")
            return {"valid": True, "reasoning": "Error occurred, proceeding."}

    def create_reflexive_graph(self, engine):
        """
        Creates a LangGraph representing the Auto-Finish loop.
        """
        def process_frame(state: AgentState):
            idx = state["idx"]
            if idx >= len(state["frames"]):
                return state
                
            result = engine.generate_frame_candidates(
                state["project_dir"], 
                idx, 
                state["prompt"], 
                state["context"], 
                state["history"], 
                fps=state["fps"], 
                story_plan=state["story_plan"]
            )
            top_candidate = result["candidates"][0]

            item = {
                "timestamp": result["timestamp"],
                "narration": top_candidate["narration"],
                "overlay": top_candidate["overlay"]
            }

            if state["transcript"] and state["transcript"][-1]["narration"] == item["narration"]:
                pass
            else:
                state["transcript"].append(item)
                state["history"].append(item["narration"])
                state["frames_since_last_review"] += 1
                
            # Limit transcript to every 10 video seconds
            advance_frames = max(1, int(10 * state["fps"]))
            state["idx"] += advance_frames
            state["is_valid"] = True
            
            return state

        def critic_review(state: AgentState):
            if not state["story_plan"] or state["frames_since_last_review"] < 5:
                state["is_valid"] = True
                return state
                
            review_res = self.reflexive_review(state["transcript"][-5:], state["story_plan"])
            state["is_valid"] = review_res.get("valid", True)
            
            if not state["is_valid"]:
                print(f"Reflexive Critic caught drift: {review_res.get('reasoning')}. Backtracking 2 generated segments.", flush=True)
                if len(state["transcript"]) > 2:
                    state["transcript"] = state["transcript"][:-2]
                    state["history"] = state["history"][:-2]
                    advance_frames = max(1, int(10 * state["fps"]))
                    state["idx"] = max(0, state["idx"] - (2 * advance_frames))
            
            state["frames_since_last_review"] = 0
            return state

        def router(state: AgentState) -> str:
            if state["idx"] >= len(state["frames"]):
                return END
            if state["frames_since_last_review"] >= 5 and state["story_plan"]:
                return "critic"
            return "process"
            
        def critic_router(state: AgentState) -> str:
            if state["idx"] >= len(state["frames"]):
                return END
            return "process"

        workflow = StateGraph(AgentState)
        workflow.add_node("process", process_frame)
        workflow.add_node("critic", critic_review)
        workflow.set_entry_point("process")
        workflow.add_conditional_edges("process", router, {"critic": "critic", "process": "process", END: END})
        workflow.add_conditional_edges("critic", critic_router, {"process": "process", END: END})
        
        return workflow.compile()
