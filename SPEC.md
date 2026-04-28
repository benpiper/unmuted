# unmuted

## Goal

I've recorded screen captures and want to turn them into technical how-to videos fit for public consumption. The videos were recorded without audio. I want to generate a timestamped transcript to narrate what I'm doing and what's happening in the video. This transcript can be used to record a live voiceover, or to auto generate a voiceover. I also want to add some text overlays to highlight important information. 

## Input

- A directory of video files with an implicit order (by date or alphanumeric order)
- A prompt to indicate the topic of the video series, the goal of the video, the starting state, and the end state. This will guide the description of each step in the video.

## Output

- A timestamped transcript file (e.g., JSON or WebVTT) that contains AI-generated narration and suggested text overlays.
- Editable transcript and overlay data that can be reviewed, adjusted, saved, and exported from the web interface.
- Synchronized video review so transcript segments can be evaluated against the source recording timeline.
- Export artifacts for downstream publishing workflows, including transcript files, chapter markers, synthesized narration audio, and rendered video as supported by the implementation.

Roadmap status is tracked in `README.md`.

## System Architecture

- **Interface**: A local Web Application that allows the user to review, edit, and approve the AI-generated transcript and overlays before any further processing or rendering. All actions must be available in the web interface, including uploading and viewing videos, viewing, editing, and downloading transcripts, and viewing and downloading chapter markers. Content should fit comfortably on a 1920x1080 display.
- **Hardware Constraints**: Must be capable of running locally on a system with a single CUDA GPU (12 GB VRAM max). This requires careful selection of Vision-Language Models (VLM) or OCR pipelines that fit within these resource constraints (e.g., quantized versions of models like LLaVA, Qwen-VL, or similar). If such a system isn't available, there must be the option to use a remote API (e.g., OpenAI, Anthropic, Google) to perform the analysis.
- **Video Analysis**: The AI must effectively understand both the graphical elements (images/UI) and the text present on the screen to properly deduce the actions. A two-phase approach:
  - **Planning Phase**: Identify tools, research them, and generate a one-sentence-per-phase story plan and narrative synopsises. Users can edit the plan before proceeding.
  - **Narration Phase**: Frame-by-frame analysis with full tool and phase context. The VLM understands which tool is active in each frame and correctly classifies user input (text in editors) vs system output. By default, frame analysis occurs every 3 seconds (configurable). The generated narration must be written in the **first-person plural** perspective (e.g., "We are typing..."), focusing on visual actions with appropriate abstraction (avoid granular details like version numbers unless critical).
- **Timestamp Generation**: To prevent LLM hallucination during drafting, the AI model must *not* generate timestamps. The backend application programmatically defines the exact timestamp associated with each transcription block based on the underlying extracted video frame interval. During the optional Optimization phase, the AI may prune overlapping timestamps to merge continuous sequences.
- **Chapter Export**: Generated chapter markers exclusively utilize the short `overlay` text formatted natively in Title Case, deduplicating consecutive identical segments to guarantee a clean YouTube-style reference list.
- **Audio Synthesis**: Voiceover generation uses a Text-to-Speech (TTS) engine. Similar to the Vision model, the web app should allow users to configure either a local model or a high-quality remote API (e.g., ElevenLabs, OpenAI TTS).
- **Containerization**: Docker & Docker Compose support for orchestrated, platform-independent deployments (Backend Python/FastAPI and Frontend React/Nginx).

## Workflow

1. **Frame Extraction & Tool Identification**: The system extracts sample keyframes from the entire video and uses a Vision-Language Model to identify all tools, technologies, programming languages, and platforms visible in the recording. For each identified tool, the system performs web search (via DuckDuckGo) to gather additional context. This ensures the planning agents understand the technical environment.

2. **Strategic Planning Pass**: The system analyzes the extracted keyframes using the identified tool context. The Strategic Planner generates a one-sentence-per-phase **Story Plan** describing the high-level objectives and which tools are involved in each phase. Users review, edit, and can delete unwanted tasks before proceeding.

3. **Synopsis Generation**: Three distinct **narrative synopsises** (one sentence each, no fluff) are generated from the story plan. Each emphasizes a different perspective (technical outcome, tools used, problem solved). The user selects the most appropriate synopsis to guide frame analysis.

4. **Frame-by-Frame Analysis**: The configured AI Vision-Language Model analyzes frames iteratively. For each frame, it receives:
   - The **Story Plan** phases to understand context and current progression
   - The selected **Synopsis** for narrative guidance
   - **Tool Context** (which tools are identified in the video) so it can correctly interpret actions
   - A **3-frame sliding visual window** (Previous, Current, Next) for visual context
   - **Phase inference**: The VLM identifies which story plan phase the current frame belongs to based on visual content
   - A rolling history of the user's recent selections to maintain sequence coherence

5. **Drafting with Tool Awareness**: The AI generates exactly 3 distinct candidate narrations per frame. Critically, the VLM uses tool context to correctly classify actions:
   - If Claude Code is active: text in editor = user-typed prompt (not a system message)
   - If terminal is active: commands = user input; output below = system response
   - If IDE is active: text in editor = user code input
   - This prevents confusion between user input and system-generated content.

6. **Human Review (Interactive Co-Pilot)**: The user steps through the video frame-by-frame in the Web App. For each frame, the user selects the best AI candidate (or edits). This selection is immediately fed back to the AI context for the next frame.

7. **Agentic Auto-Finish**: The user may opt to "Auto-Finish" at any time. The backend orchestrates a formalized **LangGraph State Machine**:
   - Sequentially generates narrations while running a **Reflexive Critic Agent** every N frames
   - The Critic evaluates recent outputs against the Story Plan
   - If narrative drift or hallucination is detected, the agent rewinds state indices, prunes bad steps, and re-evaluates
   - Enforces one transcript per 10 seconds of video

8. **Timeline Optimization**: Users can optionally trigger an AI Optimization pass. A text-only LLM phase reads the generated narrative, identifying and merging redundant or overlapping timestamps.

9. **Live Playback Sync**: Users can play the source video in a side-by-side dashboard. The generated transcript automatically highlights and scrolls to track active narration in real time.

10. **Rendering**: Based on the approved transcript, the system applies text overlays, synthesizes voiceover, and renders final publishing artifacts as supported by the implementation.

## Data Privacy & Security

Technical screen captures frequently contain sensitive data (e.g., private source code, API keys, internal dashboards). If the user opts to use a remote API (like OpenAI or Anthropic) rather than the local VLM fallback, the system should make this privacy tradeoff clear, potentially offering a way to obscure specific zones in future iterations.

## Project Organization

A "Project" is established by selecting the input video directory. All artifacts generated throughout the workflow (extracted keyframes, draft transcripts, synthesized audio tracks, and the final output MP4) should be saved directly into this parent directory (or a dedicated `.unmuted` subfolder). This keeps all related assets grouped and easily portable.

Use uv for Python dependency management.

## Error handling

Failure modes should be clearly indicated. If unable to connect to a model, or if one isn't configured, mock outputs should be obvious to the user.

## Database Persistence

Project metadata, transcript segments, and job records are persisted in a SQLite database (`unmuted.db`) using SQLAlchemy with async support (`aiosqlite`). Heavy binary assets (videos, extracted frames) remain on the filesystem in the project's `.unmuted` subfolder. This hybrid approach keeps the database small while ensuring session state survives server restarts. The SQLAlchemy ORM abstraction allows future migration to PostgreSQL by changing a single `DATABASE_URL` environment variable.

## VLM Response Caching

An in-memory LRU cache stores VLM API responses keyed by a SHA-256 hash of the frame image bytes combined with the text prompt/context. Re-analyzing a previously processed frame with the same parameters returns instantly without an API call. The cache is thread-safe, configurable via `VLM_CACHE_MAX_SIZE` (default: 500 entries), and exposes statistics at `GET /api/cache/stats`.
