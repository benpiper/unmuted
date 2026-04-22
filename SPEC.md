# unmuted

## Goal

I've recorded screen captures and want to turn them into technical how-to videos fit for public consumption. The videos were recorded without audio. I want to generate a timestamped transcript to narrate what I'm doing and what's happening in the video. This transcript can be used to record a live voiceover, or to auto generate a voiceover. I also want to add some text overlays to highlight important information. 

## Input

- A directory of video files with an implicit order (by date or alphanumeric order)
- A prompt to indicate the topic of the video series, the goal of the video, the starting state, and the end state. This will guide the description of each step in the video.

## Output

- **MVP**: A timestamped transcript file (e.g., JSON or WebVTT) that contains the AI-generated narration and suggested text overlays.
- **Future Milestone 1**: A final rendered MP4 video combining the original screen capture with the finalized text overlays inserted at key moments.
- **Future Milestone 2**: The final generated voiceover integrated into the composed MP4.

## System Architecture

- **Interface**: A local Web Application that allows the user to review, edit, and approve the AI-generated transcript and overlays before any further processing or rendering. All actions must be available in the web interface, including uploading and viewing videos, viewing, editing, and downloading transcripts, and viewing and downloading chapter markers. Content should fit comfortably on a 1920x1080 display.
- **Hardware Constraints**: Must be capable of running locally on a system with a single CUDA GPU (12 GB VRAM max). This requires careful selection of Vision-Language Models (VLM) or OCR pipelines that fit within these resource constraints (e.g., quantized versions of models like LLaVA, Qwen-VL, or similar). If such a system isn't available, there must be the option to use a remote API (e.g., OpenAI, Anthropic, Google) to perform the analysis.
- **Video Analysis**: The AI must effectively understand both the graphical elements (images/UI) and the text present on the screen to properly deduce the actions happening in the video. By default, frame analysis should occur every 3 seconds, but this interval must be configurable by the user. The generated narration must be written in the **first-person plural** perspective (e.g., "We are typing..."), focusing strictly on visual actions rather than assumed text cues.
- **Timestamp Generation**: To prevent LLM hallucination during drafting, the AI model must *not* generate timestamps. The backend application programmatically defines the exact timestamp associated with each transcription block based on the underlying extracted video frame interval. During the optional Optimization phase, the AI may prune overlapping timestamps to merge continuous sequences.
- **Chapter Export**: Generated chapter markers exclusively utilize the short `overlay` text formatted natively in Title Case, deduplicating consecutive identical segments to guarantee a clean YouTube-style reference list.
- **Audio Synthesis (Future)**: Voiceover generation will eventually require a Text-to-Speech (TTS) engine. Similar to the Vision model, the web app should allow users to configure either a local model or a high-quality remote API (e.g., ElevenLabs, OpenAI TTS).
- **Containerization**: Docker & Docker Compose support for orchestrated, platform-independent deployments (Backend Python/FastAPI and Frontend React/Nginx).

## Workflow

1. **Extraction**: The system reads the ordered video files and extracts keyframes at a suitable interval.
2. **Analysis**: The configured AI Vision-Language Model analyzes the frames iteratively. For each step, it receives a **3-frame sliding visual window** (Previous, Current, Next) and a rolling history of the user's recent instructions to maintain strict sequence context.
3. **Drafting**: The AI generates exactly 3 distinct candidate narrations and text overlays per frame.
4. **Human Review (Interactive Co-Pilot)**: The user steps through the video iteratively in the Web App. For each frame, the user selects the best AI candidate (or edits their own). This selection is immediately fed back into the AI to strictly align the context for the subsequent frame. The user may opt to "Auto-Finish" the rest of the video at any time.
5. **Timeline Optimization**: Once a draft timeline is completed, users can optionally trigger an AI Optimization pass. This secondary text-only LLM phase reads the entire generated narrative, identifying and merging redundant, repetitive, or overlapping timestamps (e.g., merging "00:00:00" and "00:00:05" if the user spends 10 seconds performing a single action).
6. **Live Playback Sync**: Upon completion, users can play the source video in a side-by-side dashboard, where the generated transcript automatically highlights and scrolls to track the active narration sequentially.
7. **Rendering (Future)**: Based on the approved transcript, the system applies the text overlays, synthesizes the voiceover, and uses `ffmpeg` (or similar) to render the final edited MP4.

## Data Privacy & Security

Technical screen captures frequently contain sensitive data (e.g., private source code, API keys, internal dashboards). If the user opts to use a remote API (like OpenAI or Anthropic) rather than the local VLM fallback, the system should make this privacy tradeoff clear, potentially offering a way to obscure specific zones in future iterations.

## Project Organization

A "Project" is established by selecting the input video directory. All artifacts generated throughout the workflow (extracted keyframes, draft transcripts, synthesized audio tracks, and the final output MP4) should be saved directly into this parent directory (or a dedicated `.unmuted` subfolder). This keeps all related assets grouped and easily portable.

Use uv for Python dependency management.

## Error handling

Failure modes should be clearly indicated. If unable to connect to a model, or if one isn't configured, mock outputs should be obvious to the user.