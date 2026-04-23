import os
import json
import shutil
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

active_projects = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    for req_dir in active_projects:
        frames_dir = Path(req_dir) / ".unmuted" / "frames"
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Accept-Ranges", "Content-Range", "Content-Length", "Content-Type"],
)

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
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
                headers={"Access-Control-Allow-Origin": request.headers.get("origin", "*")},
            )
    return await call_next(request)

class ScanRequest(BaseModel):
    directory_path: str
    interval: int = 3

@app.post("/api/project/scan")
def scan_project(req: ScanRequest):
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

class PlanRequest(BaseModel):
    directory_path: str
    prompt: str = ""
    context: str = ""

@app.post("/api/project/plan")
def generate_plan(req: PlanRequest):
    try:
        videos = scan_directory_for_videos(req.directory_path)
        if not videos:
            raise ValueError("No videos found")
            
        planning_frames_dir = os.path.join(req.directory_path, ".unmuted", "plan_frames")
        os.makedirs(planning_frames_dir, exist_ok=True)
        
        total_duration = sum([get_video_duration(v) for v in videos])
        target_frames = 10
        plan_fps = target_frames / total_duration if total_duration > 0 else 1.0
        
        start_idx = 1
        for i, video in enumerate(videos):
            clear_dir = (i == 0)
            extracted_count = extract_keyframes(video, planning_frames_dir, fps=plan_fps, clear=clear_dir, start_idx=start_idx)
            start_idx += extracted_count
            
        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        agent = TechnicalAgent(provider=provider, model=model)
        result = agent.generate_story_plan(req.directory_path, req.prompt, req.context)
        return {"success": True, "plan": result.get("plan", [])}
    except Exception as e:
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
    try:
        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")
        engine = VLMEngine(provider=provider, model=model)

        result = engine.generate_frame_candidates(req.directory_path, req.frame_index, req.prompt, req.context, req.history, fps=req.fps, story_plan=req.story_plan, use_rag=req.use_rag, rag_max_frames=req.rag_max_frames, generate_overlay=req.generate_overlay)
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
            "rag_max_frames": req.rag_max_frames
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
