import os
import json
import base64
from backend.vlm_engine import VLMEngine

with open("dummy.jpg", "wb") as f:
    f.write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="))

engine = VLMEngine(provider="openai", model="gpt-4o")
# Force bypass mock but use dummy key so it throws auth error rather than mock returning immediately
os.environ["OPENAI_API_KEY"] = "sk-fake"

print("--- Testing 1 Frame ---")
engine.generate_transcript(["dummy.jpg"], "Test")

print("\n--- Testing 2 Frames (Rolling Context) ---")
engine.generate_transcript(["dummy.jpg", "dummy.jpg"], "Test")

