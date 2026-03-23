import base64
import json
import os
from typing import List, Dict, Any

from openai import OpenAI

from prompts import VLM_SYSTEM_PROMPT, VLM_USER_PROMPT_TEMPLATE

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

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_frame_candidates(self, project_dir: str, current_index: int, prompt: str, context: str, history: List[str], fps: float = 0.5) -> Dict[str, Any]:
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
            
        messages = [
            {
                "role": "system",
                "content": VLM_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VLM_USER_PROMPT_TEMPLATE.format(prompt=prompt, env_context=env_context, history_context=history_context)},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
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
                    "detail": "low"
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
                    "detail": "low"
                }
            })

        if (os.getenv("OPENAI_API_KEY") is None and self.provider == "openai") or self.provider == "mock":
            return self._mock_candidates_response(time_str)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={ "type": "json_object" },
                max_tokens=600,
                temperature=0.7 # Increased temperature for candidate variance
            )
            
            raw_content = response.choices[0].message.content
            if os.getenv("DEBUG_VLM", "false").lower() == "true":
                print(f"=== DEBUG VLM FRAME {time_str} RAW RESPONSE ===")
                print(raw_content)
                
            data = json.loads(raw_content)
            candidates = data.get("candidates", [])
            
            if not candidates or not isinstance(candidates, list):
                candidates = [{"narration": data.get("narration", "Fallback text"), "overlay": data.get("overlay", "Fallback Overlay")}]
                
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
                {"narration": f"[{time_str}] Candidate 1: Let's review the menu options.", "overlay": "Review options"},
                {"narration": f"[{time_str}] Candidate 2: I'll click on the top setting.", "overlay": "Selecting setting"},
                {"narration": f"[{time_str}] Candidate 3: Wait for the next screen to load.", "overlay": "Loading"}
            ]
        }
