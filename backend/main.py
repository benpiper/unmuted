import os
import json
import shutil
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Request
import uuid
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import time

from scanner import scan_directory_for_videos
from extractor import extract_keyframes, get_video_duration
from vlm_engine import VLMEngine
from agents import TechnicalAgent
from contextlib import asynccontextmanager
from prompts import SYNOPSIS_GENERATION_PROMPT, TOOL_IDENTIFICATION_PROMPT
from openai import OpenAI
from ddgs import DDGS
from logging_config import setup_logging, get_logger

# Initialize logging
log_level = logging.DEBUG if os.getenv("DEBUG_VLM") == "true" else logging.INFO
json_logging = os.getenv("JSON_LOGS", "true").lower() == "true"
setup_logging(log_level=log_level, json_format=json_logging)
logger = get_logger(__name__)

active_projects = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    for req_dir in active_projects:
        frames_dir = Path(req_dir) / ".unmuted" / "frames"
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)

app = FastAPI(
    title="Unmuted API",
    description="AI-powered video narration and transcript generation API. Analyzes screen recordings and generates timestamped transcripts with text overlays.",
    version="1.0.0",
    contact={
        "name": "Unmuted Support",
        "url": "https://github.com/benpiper/unmuted",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Accept-Ranges", "Content-Range", "Content-Length", "Content-Type"],
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests and responses."""
    logger.info(f"{request.method} {request.url.path}", extra={
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else "unknown",
    })
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}", extra={
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
    })
    return response


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    auth_tokens_env = os.getenv("AUTH_TOKENS", "")
    if auth_tokens_env:
        valid_tokens = {t.strip() for t in auth_tokens_env.split(",") if t.strip()}
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = request.query_params.get("token", "")
        if token not in valid_tokens:
            logger.warning(f"Unauthorized access attempt to {request.url.path}", extra={
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            })
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
                headers={"Access-Control-Allow-Origin": request.headers.get("origin", "*")},
            )
    return await call_next(request)

class ScanRequest(BaseModel):
    """Request to scan a directory for video files."""
    directory_path: str
    interval: int = 3

@app.post("/api/project/scan")
def scan_project(req: ScanRequest):
    """
    Scan a directory for video files.

    Returns a list of video files (.mp4, .mkv, .mov, .avi, .webm) found in the directory.
    Videos are returned in alphanumeric order.

    Args:
        req: ScanRequest containing directory_path to scan

    Returns:
        dict with videos list: {"videos": [file1, file2, ...]}
    """
    try:
        videos = scan_directory_for_videos(req.directory_path)
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/project/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        workspace_id = str(uuid.uuid4())
        workspace_dir = Path("workspaces") / workspace_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = workspace_dir / file.filename
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "success": True,
            "directory_path": str(workspace_dir.absolute()),
            "video_filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/video")
def get_video(directory_path: str, request: Request):
    dir_path = Path(directory_path)
    if not dir_path.exists():
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    videos = [f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in {'.mp4', '.mkv', '.mov', '.avi', '.webm'}]
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found")
        
    video_path = videos[0]
    mtype = "video/webm" if video_path.suffix.lower() == ".webm" else "video/mp4"
    return FileResponse(
        str(video_path), 
        media_type=mtype, 
        headers={"Accept-Ranges": "bytes"}
    )

class ExtractRequest(BaseModel):
    directory_path: str
    interval: int = 3

class FrameRequest(BaseModel):
    directory_path: str
    prompt: str = ""
    context: str = ""
    frame_index: int
    history: List[str]
    fps: float
    story_plan: List[str] = []
    use_rag: bool = False
    rag_max_frames: int = 3
    generate_overlay: bool = True
    synopsis: str = ""
    tools_context: str = ""

class AutoFinishRequest(BaseModel):
    directory_path: str
    prompt: str = ""
    context: str = ""
    start_frame_index: int
    history: List[str]
    fps: float
    current_transcript: List[Dict[str, Any]]
    story_plan: List[str] = []
    use_rag: bool = False
    rag_max_frames: int = 3
    generate_overlay: bool = True
    synopsis: str = ""
    tools_context: str = ""

class PlanRequest(BaseModel):
    directory_path: str
    prompt: str = ""
    context: str = ""
    tool_context: str = ""

class SynopsisRequest(BaseModel):
    story_plan: List[str]
    prompt: str = ""
    tool_context: str = ""

class ToolsRequest(BaseModel):
    directory_path: str

@app.post("/api/project/identify-tools")
def identify_tools(req: ToolsRequest):
    try:
        planning_frames_dir = os.path.join(req.directory_path, ".unmuted", "plan_frames")
        if not os.path.exists(planning_frames_dir):
            return {"success": True, "tools": [], "tool_context": ""}

        frames = sorted([f for f in os.listdir(planning_frames_dir) if f.endswith(".jpg")])
        if not frames:
            return {"success": True, "tools": [], "tool_context": ""}

        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        engine = VLMEngine(provider=provider, model=model)

        import base64
        sample_frames = frames[::max(1, len(frames)//3)][:3]
        base64_frames = []

        for frame in sample_frames[:3]:
            frame_path = os.path.join(planning_frames_dir, frame)
            with open(frame_path, "rb") as f:
                base64_frames.append(base64.b64encode(f.read()).decode('utf-8'))

        messages = [
            {
                "role": "system",
                "content": TOOL_IDENTIFICATION_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify all tools, technologies, and systems visible in these keyframes from a technical video."}
                ]
            }
        ]

        for i, b64 in enumerate(base64_frames):
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}
            })

        if os.getenv("OPENAI_API_KEY") is None or provider == "mock":
            return {
                "success": True,
                "tools": [
                    {"name": "Python", "context": "Programming language", "confidence": "high"},
                    {"name": "Docker", "context": "Containerization", "confidence": "high"}
                ],
                "tool_context": "This video uses Python for scripting and Docker for containerization."
            }

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        tools = result.get("tools", [])

        tool_names = [t.get("name", "") for t in tools if t.get("confidence") in ["high", "medium"]]
        tool_context = ""

        if tool_names:
            try:
                ddgs = DDGS()
                search_query = " ".join(tool_names[:3])
                results = ddgs.text(f"what is {search_query} used for in software development", max_results=2)
                if results:
                    summaries = [r.get("body", "") for r in results]
                    tool_context = " ".join(summaries[:2])
            except Exception as e:
                print(f"Error researching tools: {e}", flush=True)
                tool_context = f"Tools identified: {', '.join(tool_names)}"

        return {
            "success": True,
            "tools": tools,
            "tool_context": tool_context
        }
    except Exception as e:
        print(f"Error identifying tools: {str(e)}", flush=True)
        return {"success": True, "tools": [], "tool_context": ""}

@app.post("/api/project/plan")
def generate_plan(req: PlanRequest):
    try:
        logger.info("Starting story plan generation", extra={
            "directory_path": req.directory_path,
            "has_prompt": bool(req.prompt),
            "has_context": bool(req.context),
            "has_tool_context": bool(req.tool_context)
        })

        videos = scan_directory_for_videos(req.directory_path)
        if not videos:
            logger.error("No videos found", extra={"directory_path": req.directory_path})
            raise ValueError("No videos found")

        logger.info(f"Found {len(videos)} video(s)", extra={"directory_path": req.directory_path})

        planning_frames_dir = os.path.join(req.directory_path, ".unmuted", "plan_frames")
        os.makedirs(planning_frames_dir, exist_ok=True)

        total_duration = sum([get_video_duration(v) for v in videos])
        target_frames = 10
        plan_fps = target_frames / total_duration if total_duration > 0 else 1.0

        logger.info(f"Extracting keyframes", extra={
            "total_duration_sec": total_duration,
            "target_frames": target_frames,
            "fps": plan_fps
        })

        start_idx = 1
        for i, video in enumerate(videos):
            clear_dir = (i == 0)
            extracted_count = extract_keyframes(video, planning_frames_dir, fps=plan_fps, clear=clear_dir, start_idx=start_idx)
            start_idx += extracted_count

        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        agent = TechnicalAgent(provider=provider, model=model)

        logger.info("Calling story plan agent", extra={"provider": provider, "model": model})
        result = agent.generate_story_plan(req.directory_path, req.prompt, req.context, req.tool_context)

        plan = result.get("plan", [])
        logger.info(f"Story plan generated with {len(plan)} phases", extra={"phase_count": len(plan)})

        return {"success": True, "plan": plan}
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}", extra={"error_type": type(e).__name__}, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/synopsises")
def generate_synopsises(req: SynopsisRequest):
    try:
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key is None:
            print("No OPENAI_API_KEY found, returning mock synopsises", flush=True)
            return {
                "success": True,
                "synopsises": [
                    "[MOCK] This video demonstrates a complete workflow from setup through deployment.",
                    "[MOCK] The video walks through the problem-solving process step by step.",
                    "[MOCK] The video explains the architectural and conceptual foundation of the task."
                ]
            }

        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        client = OpenAI(api_key=api_key)

        plan_text = "\n".join(req.story_plan)
        print(f"Generating synopsises for plan with {len(req.story_plan)} steps", flush=True)

        messages = [
            {
                "role": "system",
                "content": SYNOPSIS_GENERATION_PROMPT
            },
            {
                "role": "user",
                "content": f"Strategic Plan:\n{plan_text}\n\nTools/Technologies Identified:\n{req.tool_context}\n\nVideo Description: {req.prompt}"
            }
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.7
        )

        result = json.loads(response.choices[0].message.content)
        synopsises = result.get("synopsises", [])
        print(f"Generated {len(synopsises)} synopsises", flush=True)

        return {"success": True, "synopsises": synopsises}
    except Exception as e:
        print(f"Error generating synopsises: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/frame_image")
def get_frame_image(directory_path: str, frame_index: int):
    out_dir = Path(directory_path) / ".unmuted" / "frames"
    file_path = out_dir / f"frame_{frame_index + 1:04d}.jpg"
    
    max_wait = 30
    waited = 0
    while not file_path.exists() and waited < max_wait:
        time.sleep(1)
        waited += 1
        
    if file_path.exists():
        return FileResponse(str(file_path))
    else:
        raise HTTPException(status_code=404, detail="Frame not found")

@app.post("/api/project/extract")
def extract_project(req: ExtractRequest, background_tasks: BackgroundTasks):
    """
    Extract keyframes from videos and run strategic planning.

    Extracts frames from all videos in the directory at the specified interval.
    This runs asynchronously in the background. Returns immediately with total frame count.

    Args:
        req: ExtractRequest with directory_path and interval (seconds between frames)

    Returns:
        dict: {"success": true, "total_frames": N, "fps": frame_rate}
    """
    try:
        active_projects.add(req.directory_path)
        out_dir = Path(req.directory_path) / ".unmuted" / "frames"
        videos = scan_directory_for_videos(req.directory_path)
        if not videos:
            raise ValueError("No videos found")

        fps = 1.0 / req.interval

        total_duration = 0.0
        for v in videos:
            total_duration += get_video_duration(v)

        expected_frames = int(total_duration * fps)
        if expected_frames == 0:
            expected_frames = 1

        def background_extraction():
            start_idx = 1
            for i, video in enumerate(videos):
                clear_dir = (i == 0)
                extracted_count = extract_keyframes(video, str(out_dir), fps=fps, clear=clear_dir, start_idx=start_idx)
                start_idx += extracted_count

        background_tasks.add_task(background_extraction)

        return {
            "success": True,
            "total_frames": expected_frames,
            "fps": fps
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/project/frame_candidates")
def frame_candidates(req: FrameRequest):
    """
    Generate narration candidates for a single frame.

    Returns 3 distinct candidate narrations and text overlays for the specified frame.
    Uses a 3-frame sliding window (previous, current, next) for context.
    Supports optional RAG (retrieval-augmented generation) for technical context.

    Args:
        req: FrameRequest with frame_index, history, prompt, context, etc.

    Returns:
        dict: {"success": true, "data": {"timestamp": "HH:MM:SS", "candidates": [...]}}
    """
    try:
        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        engine = VLMEngine(provider=provider, model=model)

        result = engine.generate_frame_candidates(req.directory_path, req.frame_index, req.prompt, req.context, req.history, fps=req.fps, story_plan=req.story_plan, use_rag=req.use_rag, rag_max_frames=req.rag_max_frames, generate_overlay=req.generate_overlay, synopsis=req.synopsis, tools_context=req.tools_context)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/auto_finish")
def auto_finish_project(req: AutoFinishRequest):
    try:
        frames_dir = os.path.join(req.directory_path, ".unmuted", "frames")
        frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(".jpg")])

        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        engine = VLMEngine(provider=provider, model=model)
        agent = TechnicalAgent(provider=provider, model=model)

        print(f"auto_finish: starting at frame {req.start_frame_index}, total frames: {len(frames)}", flush=True)

        graph = agent.create_reflexive_graph(engine)
        
        initial_state = {
            "project_dir": req.directory_path,
            "frames": frames,
            "idx": req.start_frame_index,
            "transcript": list(req.current_transcript),
            "history": list(req.history),
            "story_plan": req.story_plan,
            "fps": req.fps,
            "prompt": req.prompt,
            "context": req.context,
            "frames_since_last_review": 0,
            "is_valid": True,
            "use_rag": req.use_rag,
            "rag_max_frames": req.rag_max_frames,
            "synopsis": req.synopsis,
            "tools_context": req.tools_context,
            "generate_overlay": req.generate_overlay
        }
        
        final_state = graph.invoke(initial_state)
        
        print(f"auto_finish: completed, final transcript length: {len(final_state['transcript'])}", flush=True)
        return {"success": True, "transcript": final_state["transcript"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class OptimizeRequest(BaseModel):
    transcript: List[Dict[str, Any]]

@app.post("/api/project/optimize")
def optimize_project(req: OptimizeRequest):
    try:
        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        engine = VLMEngine(provider=provider, model=model)
        
        optimized = engine.optimize_transcript(req.transcript)
        return {"success": True, "transcript": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SaveRequest(BaseModel):
    directory_path: str
    transcript: List[Dict[str, Any]]

def generate_vtt(transcript: list) -> str:
    lines = ["WEBVTT\n\n"]
    for i, item in enumerate(transcript):
        start_time = item["timestamp"]
        if "." not in start_time:
             start_time += ".000"
        
        end_time = "00:00:00.000"
        if i + 1 < len(transcript):
             end_time = transcript[i+1]["timestamp"]
             if "." not in end_time:
                 end_time += ".000"
        else:
             h, m, s = start_time.split(":")
             s_sec, s_ms = s.split(".")
             total_s = int(h)*3600 + int(m)*60 + int(s_sec) + 3
             h_out, rem = divmod(total_s, 3600)
             m_out, s_out = divmod(rem, 60)
             end_time = f"{h_out:02d}:{m_out:02d}:{s_out:02d}.{s_ms}"
             
        narration = item.get("narration", "")
        lines.append(f"{start_time} --> {end_time}")
        lines.append(f"{narration}\n")
    return "\n".join(lines)

@app.post("/api/project/save")
def save_project(req: SaveRequest):
    try:
        unmuted_dir = os.path.join(req.directory_path, ".unmuted")
        os.makedirs(unmuted_dir, exist_ok=True)
        
        json_path = os.path.join(unmuted_dir, "transcript.json")
        with open(json_path, "w") as f:
            json.dump({"transcript": req.transcript}, f, indent=2)
            
        vtt_path = os.path.join(unmuted_dir, "transcript.vtt")
        with open(vtt_path, "w") as f:
            f.write(generate_vtt(req.transcript))
            
        # Clean up frames since everything is fully saved
        frames_dir = os.path.join(req.directory_path, ".unmuted", "frames")
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir, ignore_errors=True)
            
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/download/{file_type}")
def download_artifact(directory_path: str, file_type: str):
    unmuted_dir = Path(directory_path) / ".unmuted"
    if not unmuted_dir.exists():
        raise HTTPException(status_code=404, detail="Transcript not generated yet")
        
    if file_type == "json":
        file_path = unmuted_dir / "transcript.json"
        media_type = "application/json"
        filename = "transcript.json"
    elif file_type == "vtt":
        file_path = unmuted_dir / "transcript.vtt"
        media_type = "text/vtt"
        filename = "transcript.vtt"
    elif file_type == "chapters":
        file_path = unmuted_dir / "chapters.txt"
        json_path = unmuted_dir / "transcript.json"
        if not json_path.exists():
            raise HTTPException(status_code=404, detail="JSON transcript missing")
        with open(json_path) as f:
            data = json.load(f).get("transcript", [])
        
        import string
        lines = []
        last_overlay = None
        for item in data:
            overlay_text = item.get('overlay', 'Chapter Segment')
            title_case_overlay = string.capwords(overlay_text)
            
            # Prevent spamming consecutive identical chapter titles
            if title_case_overlay == last_overlay:
                continue
                
            ts = item["timestamp"].split(".")[0] if "." in item["timestamp"] else item["timestamp"]
            lines.append(f"{ts} - {title_case_overlay}")
            last_overlay = title_case_overlay
            
        with open(file_path, "w") as fw:
            fw.write("\n".join(lines))
        media_type = "text/plain"
        filename = "chapters.txt"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
        
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
    return FileResponse(str(file_path), media_type=media_type, filename=filename)
