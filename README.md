# unmuted

**Unmuted** is a local-first web application designed to turn your screen recording captures into polished, technical how-to videos fit for public consumption. It uses AI Vision-Language Models (VLMs) like OpenAI's GPT-4o, Anthropic Claude, or local Ollama instances to generate timestamped narration transcripts and text overlays by analyzing the visual UI and text in your recordings.

## Features

- **Automated Frame Extraction**: Uses `ffmpeg` to sample keyframes from your technical screen captures.
- **Tool & Technology Identification**: Automatically detects tools in use (Claude Code, Docker, Python, etc.) and enriches planning with web-researched context.
- **Strategic Planning with Synopsises**: Generates a high-level story plan and 3 narrative synopsises to guide frame-by-frame analysis.
- **Environment-Aware VLM Analysis**: Vision model understands which tools are active in each frame, correctly distinguishing user input in editors vs terminal commands.
- **High-Fidelity Text Recognition**: Uses high-detail image analysis for accurate OCR of code, commands, and UI text.
- **Agentic Auto-Finish**: Powered by a robust **LangGraph StateGraph**, the backend utilizes a Reflexive Critic agent to detect narrative drift and recursively correct mistakes during long sequences.
- **AI-Powered VLM Analysis**: Analyzes your action goals, story plan, and frame sequences to output polished transcripts and overlay suggestions.
- **Interactive Planning UI**: Review and edit the AI-generated story plan—delete unwanted tasks, add your own, before proceeding to frame analysis.
- **Stunning Review UI**: A modern Glassmorphism dashboard built with React allowing you to review and tweak transcripts in a Human-in-the-Loop workflow.

## System Overview

Unmuted utilizes a sophisticated multi-agent architecture to transform silent screen recordings into professional technical tutorials. This architecture combines specialized AI agents with a human-in-the-loop co-pilot system.

![Multi-Agent Architecture Infographic](file:///home/user/.gemini/antigravity/brain/c44fc729-3474-4807-b6a4-3e32e44d9818/multi_agent_architecture_infographic_1777405392399.png)

```mermaid
graph TD
    User([User / Co-Pilot]) -->|Inputs Prompt| UI[Frontend Review UI]
    UI -->|Triggers Action| Orch[FastAPI Orchestrator]
    
    subgraph "Preparation Agents"
        Orch --> ToolAgent[Environment Analyzer]
        ToolAgent -->|Tools/Tech Found| PlanAgent[Strategic Planner]
        PlanAgent -->|Story Plan| SynopsisAgent[Synopsis Generator]
    end
    
    PlanAgent -->|Review| UI
    SynopsisAgent -->|Selection| UI
    
    subgraph "Execution Agents (LangGraph)"
        Orch --> Narrator[Narration Generator]
        Narrator -->|Draft Segments| Critic[Reflexive Critic]
        Critic -->|Validation| Narrator
        Critic -->|Backtrack / Prune| Narrator
    end
    
    Narrator -->|Candidate Narrations| UI
    UI -->|Manual Selection| Orch
    
    subgraph "Finalization"
        Orch --> Opt[Timeline Optimizer]
        Opt -->|Clean Transcript| Output[Final VTT / JSON / MP4]
    end
```

## System Architecture & Workflow

Unmuted's workflow is split into two distinct phases:

### Phase 1: Planning (Linear Agents - Direct LLM Calls)

Before frame-by-frame processing, the system performs rapid planning using three sequential agents:

1. **The Tool Identifier**: Analyzes sample keyframes to detect all tools/technologies in use (Claude Code, Docker, Python, etc.) and researches unfamiliar ones via web search. This enriches the planning context.

2. **The Strategic Planner**: Performs a holistic scan of the entire video timeline to construct a one-sentence-per-phase "Story Plan." Uses tool context to understand what's happening in each phase. Users can review, edit, and delete plan tasks before proceeding.

3. **The Synopsis Generator**: Creates 3 distinct narrative synopsises (one sentence each, no fluff, no "in this video..." phrasing). Each emphasizes a different perspective (technical outcome, tools used, problem solved). User selects the best one to guide frame analysis.

### Phase 2: Auto-Finish (LangGraph State Machine with Reflexive Critic)

Once the user begins frame-by-frame review, the interactive processor operates frame-by-frame. When the user clicks **Resume Auto-Finish**, a LangGraph-orchestrated state machine takes over:

1. **The Processor (Drafting Agent)**: The primary LangGraph node. For each frame, it:
   - Receives the Story Plan phases (understanding current progression)
   - References the selected synopsis (narrative guidance)
   - Uses tool context to understand which application is active
   - Infers the current phase based on visual content
   - Generates 3 distinct candidate narrations using a 3-frame sliding window (Previous, Current, Next)
   - Understands that text in editors = user input, not system messages

2. **The Reflexive Critic**: A secondary evaluating node that runs every 5 processing cycles (~50 seconds of video):
   - Inspects the Processor's recent transcript backlog
   - Evaluates against the Story Plan for narrative drift or hallucination
   - If issues detected: rewinds state indices, prunes bad steps, forces re-evaluation
   - If approved: continues processing
   - Enforces one transcript per 10 seconds of video

#### Auto-Finish LangGraph State Machine

```mermaid
flowchart TD
    START((Resume Auto-Finish)) --> process[Processor: Generate Frame Candidates]
    process --> router{Processed 5 frames?}
    router -- "No, continue" --> process
    router -- "Yes, evaluate" --> critic[Reflexive Critic: Validate Transcript]
    
    critic --> check{Drift or<br/>Hallucination?}
    check -- "Yes: Rewind & Prune" --> process
    check -- "No: Approved" --> more{More frames?}
    more -- "Yes" --> process
    more -- "No" --> END((Complete))
    
    classDef default fill:#1E293B,stroke:#94A3B8,color:#F8FAFC
    classDef node fill:#3B82F6,stroke:#1D4ED8,color:#FFF,font-weight:bold
    classDef decision fill:#6366F1,stroke:#4338CA,color:#FFF
    classDef terminal fill:#10B981,stroke:#047857,color:#FFF
    
    class START,END terminal
    class process,critic node
    class router,check,more decision
```

## Requirements

- `ffmpeg` (must be installed on your system and available in your PATH)
- Node.js (v18+) and `npm`
- Python 3.10+
- `uv` (Fast Python package/project manager)

## Authentication

Unmuted uses JWT-based authentication with email/password login. The system supports a **hybrid bootstrap approach** for initializing the first admin:

**Option 1: Environment Variable Bootstrap** (recommended for deployed instances):
```bash
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure_password_here
JWT_SECRET_KEY=your-secret-key-here
```
The admin user is created automatically on startup if no users exist.

**Option 2: Setup Endpoint** (fallback for manual setup):
- If no admin exists and no env vars are provided, navigate to `/setup` to create the first admin manually
- API: `POST /api/auth/setup` with `{email, password}`
- Check system status: `GET /api/auth/status`

**For Local Development:**
Run the backend without auth env vars. You'll be guided to create an admin user via the setup endpoint when you first access the UI.

## Getting Started

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

## Usage Instructions

1. **Open the UI**: Navigate to `http://localhost:5173` in your browser.
2. **Setup Project**: Enter the absolute path to a folder containing `.mp4` or `.mkv` videos (e.g., `/home/user/unmuted`).
3. **Draft a Prompt**: Write a short prompt indicating the goal of the video (e.g., "Demonstrate how to deploy a Docker container to Kubernetes").
4. **Scan & Extract Frames**: 
   - Click **Scan Directory** to verify your videos are detected.
   - Click **Extract & Plan**. The backend will:
     - Extract keyframes via `ffmpeg`
     - Identify tools/technologies visible in the video (Claude Code, Docker, Python, etc.)
     - Generate a strategic story plan (one sentence per phase)
     - Generate 3 narrative synopsises to guide analysis
5. **Review & Edit Plan**:
   - Review the AI-generated story plan and synopsises.
   - Delete any unwanted tasks or edit existing ones.
   - Select your preferred synopsis (or the AI will use the first one).
   - Click **Begin Frame-by-Frame Review** to proceed.
6. **Interactive Review**: 
   - Step through the video frame-by-frame as the AI generates 3 distinct narration candidates.
   - The AI uses the story plan phase context, synopsis, tool information, and a sliding 3-frame window to understand what you're doing.
   - Select the best candidate (or write your own) and click **Commit & Next**.
   - At any time, click **Resume Auto-Finish** to complete the remaining frames using the AI's top choices.
7. **Synchronized Playback**: After completion, press play on the side-by-side video viewer to test your flow. The interactive timeline automatically highlights and syncs narration in real time.
8. **Export**: Save the finalized transcript, then download `transcript.json`, `transcript.vtt` (WebVTT subtitle format), and YouTube chapter markers. If enabled, you can also synthesize `narration.mp3` and render `rendered.mp4`.

## Export Formats

Unmuted provides transcript, chapter, audio, and video artifacts:

**`transcript.json`**
- Complete transcript as a JSON array of narration objects
- Each object contains: `timestamp` (HH:MM:SS), `narration` (the spoken text), and `overlay` (on-screen text suggestion)
- Suitable for programmatic processing, custom tooling, or database storage
- Schema: `[{"timestamp": "00:05:30", "narration": "...", "overlay": "..."}, ...]`

**`transcript.vtt`**
- WebVTT subtitle format compatible with all major video editors and players
- Import into Premiere, Final Cut Pro, DaVinci Resolve, or web players
- Includes timing, narration text, and optional speaker labels
- Ready to embed as subtitle tracks in your final video

**`chapters.txt`**
- YouTube chapter format - one line per chapter
- Format: `HH:MM:SS - Chapter Title`
- Paste directly into the YouTube description to enable interactive chapters
- Example:
  ```
  00:00:00 - Introduction
  00:02:15 - Setting up Docker
  00:05:30 - Deploying to Kubernetes
  ```

**`narration.mp3`**
- Synthesized narration audio assembled from the saved transcript
- Generated by the TTS workflow when OpenAI TTS or ElevenLabs credentials are configured
- Timed so narration clips begin at their transcript timestamps

**`rendered.mp4`**
- Final rendered video generated with FFmpeg
- Burns transcript narration and overlay text into the source screen recording
- Uses the review UI render settings for caption color, overlay color, caption size, overlay size, and caption position

## Troubleshooting

**ffmpeg not found**
- Ensure `ffmpeg` is installed on your system and added to your PATH
- Test: run `ffmpeg -version` in your terminal — it should print version info
- On Ubuntu/Debian: `sudo apt install ffmpeg`
- On macOS: `brew install ffmpeg`
- On Windows: Download from https://ffmpeg.org/download.html

**VLM returns mock data instead of real analysis**
- Check that `OPENAI_API_KEY` is set correctly: `echo $OPENAI_API_KEY`
- Verify your API key is valid (not expired, not revoked)
- Check backend logs for authentication errors: `uv run uvicorn main:app --reload` (watch stderr)
- If using Ollama, verify `OLLAMA_BASE_URL` is correct and the Ollama server is running

**CORS error: "Access to XMLHttpRequest blocked"**
- This happens when frontend and backend are on different domains
- Set `CORS_ORIGINS` in `.env` to match your frontend URL
- Default: `CORS_ORIGINS=http://localhost:5173` (Vite dev server)
- For production: `CORS_ORIGINS=https://yourdomain.com` or `CORS_ORIGINS=https://yourdomain.com,http://localhost:5173`

**Upload fails with 413 Payload Too Large**
- Increase `MAX_UPLOAD_SIZE_MB` in `.env` (default is 500 MB)
- Example: `MAX_UPLOAD_SIZE_MB=2000` for 2 GB limit
- Note: Consider your server's available disk space and memory

**Rate limit 429 Too Many Requests**
- You've hit the per-IP rate limit (60 requests per 60 seconds by default)
- Increase limits in `.env` if needed:
  - `RATE_LIMIT_MAX_CALLS=120` (requests per window)
  - `RATE_LIMIT_WINDOW_SECONDS=60` (time window in seconds)
- Or reduce request frequency from your client

**Auto-Finish job appears stuck**
- Check job progress: `curl http://localhost:8000/api/jobs/{job_id}/status`
- Progress should increment from 0 to 100 as frames are processed
- If stuck, it may be waiting for frame files to be extracted
- Check backend logs for any error messages
- You can cancel the job: `curl -X DELETE http://localhost:8000/api/jobs/{job_id}`

## Roadmap / Milestones

This README is the canonical milestone tracker. `SPEC.md` describes requirements and architecture only.

### Core Workflow
- [x] **MVP**: Generate timestamped transcript artifacts with narration and overlay suggestions
  - [x] Save `transcript.json`
  - [x] Save `transcript.vtt`
  - [x] Generate YouTube-style `chapters.txt`

- [ ] **Milestone 1**: Final transcript editing
  - Status: Partially implemented
  - [x] Add transcript segments
  - [x] Remove transcript segments
  - [x] Modify timestamps, narration, and overlays
  - [ ] Reorder transcript segments with explicit move controls
  - [x] Export edited transcript as VTT/JSON

- [x] **Milestone 1.5**: Video-transcript synchronization in the review UI
  - [x] Video playback advances the active transcript highlight
  - [x] Active transcript segment scrolls into view during playback
  - [x] Clicking a transcript timestamp jumps video playback to that timestamp

### Phase 1: Video Output & Audio (Near Term)
- [ ] **Milestone 2**: Render final MP4 with text overlays baked in via UI timeline data
  - Status: Partially implemented
  - [x] Generate MP4 files with burned-in captions and overlay text
  - [x] Use FFmpeg for video composition
  - [x] Support caption color, overlay color, caption size, overlay size, and caption position via the review UI
  - [ ] Support custom font selection via the review UI
  - [ ] Support independent overlay positioning via the review UI
  - [ ] Include synthesized narration audio in the rendered MP4

- [ ] **Milestone 3**: Text-to-Speech audio synthesis
  - Status: Partially implemented
  - [x] Generate timed `narration.mp3` from transcript segments
  - [x] Support OpenAI TTS
  - [x] Support ElevenLabs when `ELEVENLABS_API_KEY` is configured
  - [x] Support selectable OpenAI voices from the review UI
  - [ ] Integrate local XTTS
  - [ ] Support ElevenLabs voice discovery/selection from the review UI
  - [ ] Embed synthesized audio into the final MP4 with automatic sync

### Phase 2: Production & Deployment (Medium Term)
- [x] **Milestone 4**: User authentication and authorization
  - [x] JWT authentication with email/password support
  - [x] Per-user project ownership checks
  - [x] Admin user initialization via environment variables or setup endpoint
  - [x] Admin approval flow for user accounts
  - [ ] OAuth2 support (GitHub, Google) - future
  - [ ] Role-based access control (RBAC) for team collaboration - future
  - [ ] API key management for programmatic access - future

- [ ] **Milestone 5**: Multi-tenancy and workspace management
  - Status: Partially implemented
  - [x] Isolate projects by owner account
  - [x] Create upload-backed workspace directories per project
  - [x] List projects for the current user
  - [ ] Support multiple named workspaces per user with independent configurations
  - [ ] Team collaboration with granular permission levels
  - [ ] Workspace-specific settings and customization

- [ ] **Milestone 6**: Database persistence layer
  - Status: Partially implemented
  - [x] SQLite for local development
  - [x] ORM-based schema management with SQLAlchemy
  - [x] Persist project metadata, transcript segments, and job records
  - [ ] Production-ready PostgreSQL support with async driver configuration
  - [ ] Automatic schema migrations and backups

- [ ] **Milestone 7**: Performance optimization
  - Status: Partially implemented
  - [x] In-memory LRU cache for VLM API responses
  - [x] In-process job queue for long-running auto-finish, TTS, and render jobs
  - [ ] Redis caching layer for frequently accessed data in production
  - [ ] Frame extraction and processing optimizations
  - [ ] Lazy loading and pagination for large video projects

### Phase 3: Enterprise & Compliance (Long Term)
- [x] **Milestone 8**: CI/CD pipeline and automation
  - [x] GitHub Actions for automated frontend linting and builds
  - [x] Automated backend testing with pytest
  - [ ] Docker image builds and registry pushes - future
  - [ ] Staging and production environment workflows - future

- [ ] **Milestone 9**: Infrastructure as Code
  - Status: Partially implemented
  - [x] Basic Kubernetes manifests for backend, frontend, config, and persistent workspace storage
  - [ ] Terraform configuration for AWS/GCP/Azure deployments
  - [ ] Automated scaling and load balancing
  - [ ] Monitoring and alerting setup

- [ ] **Milestone 10**: Usage tracking and billing
  - [ ] Usage metrics dashboard (videos processed, frames analyzed, API calls)
  - [ ] Tiered pricing and subscription management
  - [ ] Stripe/Paddle integration for payments

- [ ] **Milestone 11**: Admin dashboard
  - Status: Partially implemented
  - [x] User management
  - [x] Account approval
  - [x] Admin promotion/demotion
  - [ ] System health monitoring and metrics
  - [ ] Quota administration
  - [ ] Audit logs and activity tracking

- [ ] **Milestone 12**: Privacy and compliance
  - [ ] GDPR/CCPA compliance with data export and deletion
  - [ ] End-to-end encryption for sensitive projects
  - [ ] SOC 2 compliance documentation

### Phase 4: Advanced Features (Future)
- [ ] **Milestone 13**: Batch processing and scheduling
  - [ ] Queue multiple videos for processing
  - [ ] Scheduled processing during off-peak hours
  - [ ] Webhook notifications for job completion

- [ ] **Milestone 14**: Integrations and plugins
  - [ ] YouTube upload automation
  - [ ] Export to Adobe Premiere, Final Cut Pro, DaVinci Resolve
  - [ ] Zapier/Make.com integration for workflow automation

- [ ] **Milestone 15**: Model improvements and fine-tuning
  - [ ] Custom VLM fine-tuning for specialized domains
  - [ ] Support for additional open-source models
  - [ ] Accuracy improvements based on user feedback
