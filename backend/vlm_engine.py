import base64
import json
import os
from typing import List, Dict, Any

from openai import OpenAI

from prompts import VLM_SYSTEM_PROMPT, VLM_USER_PROMPT_TEMPLATE, RAG_QUERY_EXTRACTION_PROMPT
from resilience import retry, CircuitBreaker

class VLMEngine:
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model = model

        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
        elif self.provider == "ollama":
            # Ollama mapping for OpenAI endpoints
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            api_key = os.getenv("OLLAMA_API_KEY", "ollama")
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        elif self.provider == "mock":
            self.client = None
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Circuit breaker for VLM API calls
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @retry(max_attempts=3, initial_delay=2.0, max_delay=10.0)
    def _call_vlm_api(self, messages: List[Dict[str, Any]]) -> str:
        """Call VLM API with retry logic."""
        return self.circuit_breaker.call(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=600,
                temperature=0.7
            )
        )

    def generate_frame_candidates(self, project_dir: str, current_index: int, prompt: str, context: str, history: List[str], fps: float = 0.5, story_plan: List[str] = None, use_rag: bool = False, rag_max_frames: int = 3, generate_overlay: bool = True, synopsis: str = "", tools_context: str = "") -> Dict[str, Any]:
        """
        Queries the vision model for a single frame, returning 3 narration candidates.
        """
        from pathlib import Path
        import time
        
        frames_dir = Path(project_dir) / ".unmuted" / "frames"
        
        if current_index < 0:
            raise ValueError("Frame index out of bounds")
            
        video_file_index = current_index + 1
        frame_path = frames_dir / f"frame_{video_file_index:04d}.jpg"
        
        max_wait = 30
        waited = 0
        while not frame_path.exists() and waited < max_wait:
            time.sleep(1)
            waited += 1
            
        if not frame_path.exists():
            return self._mock_candidates_response("Timeout")
            
        frame_path = str(frame_path)
        
        previous_frame_path = None
        if current_index > 0:
            prev_file = frames_dir / f"frame_{video_file_index - 1:04d}.jpg"
            if prev_file.exists():
                previous_frame_path = str(prev_file)
                
        next_frame_path = None
        next_file = frames_dir / f"frame_{video_file_index + 1:04d}.jpg"
        next_wait = 10
        next_waited = 0
        while not next_file.exists() and next_waited < next_wait:
            time.sleep(1)
            next_waited += 1
            
        if next_file.exists():
            next_frame_path = str(next_file)
        
        time_sec = int(current_index / fps)
        mm, ss = divmod(time_sec, 60)
        hh, mm = divmod(mm, 60)
        time_str = f"{hh:02d}:{mm:02d}:{ss:02d}"

        base64_image = self._encode_image(frame_path)
        
        history_context = ""
        if history:
            history_context = "Recent Actions Taken:\n" + "\n".join([f"- {t}" for t in history[-10:]])
        else:
            history_context = "No prior actions. This is the start of the video."

        env_context = context if context else "None specified."

        story_plan_context = ""
        if story_plan:
            story_plan_context = "\n".join([f"{i+1}. {phase}" for i, phase in enumerate(story_plan)])
        else:
            story_plan_context = "No story plan provided. Analyze the frame independently."
            
        messages = [
            {
                "role": "system",
                "content": VLM_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VLM_USER_PROMPT_TEMPLATE.format(prompt=prompt, env_context=env_context, tools_context=tools_context, story_plan_context=story_plan_context, history_context=history_context, synopsis=synopsis)},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        if previous_frame_path:
            prev_base64 = self._encode_image(previous_frame_path)
            messages[1]["content"].insert(1, {"type": "text", "text": "PREVIOUS Frame (For Context):"})
            messages[1]["content"].insert(2, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{prev_base64}",
                    "detail": "high"
                }
            })
            messages[1]["content"].insert(3, {"type": "text", "text": "CURRENT Frame (Analyze this one):"})
            
        if next_frame_path:
            next_base64 = self._encode_image(next_frame_path)
            messages[1]["content"].append({"type": "text", "text": "NEXT Frame (For Context on what happens immediately after):"})
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{next_base64}",
                    "detail": "high"
                }
            })

        if (os.getenv("OPENAI_API_KEY") is None and self.provider == "openai") or self.provider == "mock":
            return self._mock_candidates_response(time_str)

        if use_rag and current_index < rag_max_frames and self.provider == "openai":
            print(f"Executing RAG flow for frame {current_index}...")
            from prompts import RAG_QUERY_EXTRACTION_PROMPT
            
            rag_content = []
            if previous_frame_path:
                rag_content.append({"type": "text", "text": "PREVIOUS Frame:"})
                rag_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{prev_base64}", "detail": "high"}})
                rag_content.append({"type": "text", "text": "CURRENT Frame (Extract query based on what CHANGED/was typed):"})
            else:
                rag_content.append({"type": "text", "text": "CURRENT Frame:"})

            rag_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}})
            
            rag_messages = [
                {"role": "system", "content": RAG_QUERY_EXTRACTION_PROMPT},
                {"role": "user", "content": rag_content}
            ]
            try:
                extract_resp = self.client.chat.completions.create(
                    model="gpt-4o-mini" if self.model.startswith("gpt-4o") else self.model,
                    messages=rag_messages,
                    response_format={"type": "json_object"},
                    max_tokens=60,
                    temperature=0.1
                )
                query_data = json.loads(extract_resp.choices[0].message.content)
                query = query_data.get("query", "").strip()
                
                if query:
                    print(f"Extracted RAG query: '{query}'")
                    from ddgs import DDGS
                    rag_results = DDGS().text(query, max_results=2)
                    rag_text = "\n".join([f"- {r['title']}: {r['body']}" for r in rag_results])
                    if rag_text:
                        print("Appending external RAG context to VLM.")
                        messages[1]["content"].append({
                            "type": "text", 
                            "text": f"EXTERNAL KNOWLEDGE SEARCH RESULTS FOR '{query}':\n{rag_text}\n(Use this factual context to precisely describe the technical action on screen.)"
                        })
            except Exception as e:
                print(f"RAG extraction/search failed on frame {time_str}: {e}")

        try:
            response = self._call_vlm_api(messages)
            raw_content = response.choices[0].message.content
            if os.getenv("DEBUG_VLM", "false").lower() == "true":
                print(f"=== DEBUG VLM FRAME {time_str} RAW RESPONSE ===")
                print(raw_content)
                
            data = json.loads(raw_content)
            candidates = data.get("candidates", [])
            
            if not candidates or not isinstance(candidates, list):
                candidates = [{"narration": data.get("narration", "Fallback text"), "overlay": data.get("overlay", "Fallback Overlay")}]
                
            if not generate_overlay:
                for cand in candidates:
                    cand.pop('overlay', None)
            return {
                "timestamp": time_str,
                "candidates": candidates
            }
            
        except Exception as e:
            print(f"Error calling VLM API on frame {time_str}: {e}")
            raise e

    def optimize_transcript(self, transcript_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        from prompts import LLM_OPTIMIZE_TRANSCRIPT_PROMPT
        messages = [
            {
                "role": "system",
                "content": LLM_OPTIMIZE_TRANSCRIPT_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(transcript_data, indent=2)
            }
        ]

        if (os.getenv("OPENAI_API_KEY") is None and self.provider == "openai") or self.provider == "mock":
            return transcript_data

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={ "type": "json_object" },
                max_tokens=4000,
                temperature=0.2 
            )
            
            raw_content = response.choices[0].message.content
            if os.getenv("DEBUG_VLM", "false").lower() == "true":
                print(f"=== DEBUG OPTIMIZE TRANSCRIPT RAW RESPONSE ===")
                print(raw_content)
                
            data = json.loads(raw_content)
            return data.get("transcript", transcript_data)
            
        except Exception as e:
            print(f"Error optimizing transcript: {e}")
            raise e

    def _mock_candidates_response(self, time_str: str) -> Dict[str, Any]:
        return {
            "timestamp": time_str,
            "candidates": [
                {"narration": f"[{time_str}] [MOCK OUTPUT] Let's review the menu options.", "overlay": "[MOCK] Review options"},
                {"narration": f"[{time_str}] [MOCK OUTPUT] I'll click on the top setting.", "overlay": "[MOCK] Selecting setting"},
                {"narration": f"[{time_str}] [MOCK OUTPUT] Wait for the next screen to load.", "overlay": "[MOCK] Loading"}
            ]
        }
