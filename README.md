# 🎙️ unmuted

**Unmuted** is a local-first web application designed to turn your screen recording captures into polished, technical how-to videos fit for public consumption. It uses AI Vision-Language Models (VLMs) like OpenAI's GPT-4o, Anthropic Claude, or local Ollama instances to generate timestamped narration transcripts and text overlays by analyzing the visual UI and text in your recordings.

## ✨ Features

- **Automated Frame Extraction**: Uses `ffmpeg` to sample keyframes from your technical screen captures.
- **Agentic Auto-Finish**: Powered by a robust **LangGraph StateGraph**, the backend utilizes a Reflexive Critic agent to detect narrative drift and recursively correct mistakes during long sequences.
- **AI-Powered VLM Analysis**: Reads your provided action goals and outputs actionable transcripts and overlay suggestions.
- **Stunning Review UI**: A modern Glassmorphism dashboard built with React allowing you to review and tweak transcripts in a Human-in-the-Loop workflow.

## 🧠 LangGraph Orchestration

Unmuted delegates the heavy lifting of processing continuous sequences to a formalized server-side LangGraph agent network.
This ensures strict 10-second contextual limits per extraction and implements an active Critic node that prevents the AI from wildly hallucinating when it gets confused.

The workflow is driven by three distinct AI Agent personas:
1. **The Strategic Planner**: A precursor agent that performs a high-speed holistic scan of the entire video timeline to construct a granular "Story Plan" before any frame-by-frame processing begins.
2. **The Processor (Drafting Agent)**: The primary LangGraph node. It acts iteratively on single frames using a 3-frame sliding window, referencing the Story Plan and historical actions to draft candidate narrations.
3. **The Reflexive Critic**: A secondary evaluating node in the LangGraph. It runs every 5 processing cycles (roughly every 50 seconds of video) to inspect the Processor's recent transcript backlog. If the drafted transcript severely deviates from the Story Plan, the Critic rewinds the StateGraph index, prunes the transcript, and forces the Processor to try again.

```mermaid
flowchart TD
    %% Nodes
    START((Start))
    process[Process Frame Node]
    critic[Reflexive Critic Node]
    router{State Router}
    END_NODE((End))
    
    %% Flow
    START --> process
    process --> router
    router -- "processed 5 transcripts?" --> critic
    router -- "continue" --> process
    router -- "end of frames" --> END_NODE
    
    critic -- "drift caught (rewinds index & prunes transcript)" --> process
    critic -- "approve" --> process
    critic -- "end of frames" --> END_NODE
    
    classDef default fill:#1E293B,stroke:#94A3B8,color:#F8FAFC
    classDef node fill:#3B82F6,stroke:#1D4ED8,color:#FFF,font-weight:bold
    classDef decision fill:#6366F1,stroke:#4338CA,color:#FFF
    classDef terminal fill:#10B981,stroke:#047857,color:#FFF
    
    class START,END_NODE terminal
    class process,critic node
    class router decision
```

## 🛠️ Requirements

- `ffmpeg` (must be installed on your system and available in your PATH)
- Node.js (v18+) and `npm`
- Python 3.10+
- `uv` (Fast Python package/project manager)

## 🚀 Getting Started

The application is split into a Python FastAPI Backend and a React/Vite Frontend. You must run both concurrently.

### 1. Set up the Backend (API)

Open a terminal and navigate to the project directory:

```bash
cd backend

# Option A: Use OpenAI API
export VLM_PROVIDER="openai"
export VLM_MODEL="gpt-4o"
export OPENAI_API_KEY="sk-your-openai-key"

# Option B: Use external Ollama Server (e.g. gemma3)
export VLM_PROVIDER="ollama"
export VLM_MODEL="gemma3"
export OLLAMA_BASE_URL="http://192.168.88.86:11434/v1"
export OLLAMA_API_KEY="any-key" # Ollama accepts any string

# If no API key or provider is set, the engine will return "mock" data for UI testing!

### Enabling Verbose Debugging
If you feel the AI analysis is failing or just want to see the exact LLM payload and raw response for every single frame, export the debug flag *alongside* your API keys:
```bash
export DEBUG_VLM="true"
# Then start the server
uv run uvicorn main:app --reload
```
*The raw JSON from the model will print directly to your backend terminal.*

### 2. Set up the Frontend (UI)

Open a second terminal window:

```bash
cd frontend
# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
*The UI will start on `http://localhost:5173`.*

### 3. Run with Docker (Recommended)

If you have Docker and Docker Compose installed, you can start the entire stack with a single command:

```bash
# Copy the example env file and add your API key
cp .env.example .env
# Edit .env with your VLM provider and API key, then:
docker-compose up --build
```

- The app will be available at `http://localhost:5173`.
- Your project workspaces will be persisted in `./backend/workspaces`.

### 4. Deploy to a Cloud Provider (e.g. Railway, Render, Fly.io)

The Docker Compose setup deploys anywhere that supports multi-container apps.

**Railway:**
1. Push your repo to GitHub.
2. Create a new Railway project → **Deploy from GitHub repo**.
3. Railway auto-detects `docker-compose.yml`. Set your env vars (`VLM_PROVIDER`, `VLM_MODEL`, `OPENAI_API_KEY`) in the Railway dashboard.
4. Expose the `frontend` service on a public port — Railway will give you a URL.

**Generic VPS (Ubuntu/Debian):**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
# Clone the repo and deploy
git clone <your-repo-url> && cd unmuted
cp .env.example .env && nano .env   # add your API key
docker compose up -d --build
```

> [!NOTE]
> The frontend Nginx container reverse-proxies all `/api/*` requests to the backend, so only **one port (5173)** needs to be publicly exposed.

## 🎬 Usage Instructions

1. **Open the UI**: Navigate to `http://localhost:5173` in your browser.
2. **Setup Project**: Enter the absolute path to a folder containing `.mp4` or `.mkv` videos (e.g., `/home/user/unmuted`).
3. **Draft a Prompt**: Write a short prompt indicating the goal of the video (e.g., "Demonstrate how to mount an ISO to HP iLo").
4. **Scan & Process**: 
   - Click **Scan Directory** to verify your videos are detected.
   - Click **Extract & Review Sequence**. The backend will use `ffmpeg` to asynchronously stream frames to a `.unmuted/frames` folder, instantly unlocking the Interactive Review mode.
5. **Interactive Review**: 
   - Step through the video frame-by-frame as the AI generates 3 distinct narration candidates based on a sliding 3-frame window and historical context.
   - Select the best candidate (or write your own) and click **Commit & Next** to feed your selection back into the AI.
   - At any time, you can click **Commit & Auto Finish Rest** to iteratively process the remainder of the clip using the AI's top choices in real-time.
6. **Synchronized Playback**: After completion, press play on the side-by-side video viewer to test your flow. The interactive timeline will automatically highlight and auto-scroll to match the exact timestamps of your narration frames in real time.
7. **Export**: Browse the final timeline and click **Generate Export Artifacts**. The final transcript will be directly downloaded via your browser as `transcript.json` and `transcript.vtt` (WebVTT subtitle format), alongside a strictly-formatted YouTube Chapters list.

## 🔮 Roadmap / Next Milestones

- [ ] **Milestone 1**: Render Final MP4 with text overlays baked in via UI timeline data.
- [ ] **Milestone 2**: Synthesize text-to-speech audio streams (via local XTTS or external ElevenLabs) and embed the voiceover into the final MP4.
