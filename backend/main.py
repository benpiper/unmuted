import os
import json
import shutil
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Request
import uuid
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel, Field
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
from security import validate_workspace_path, get_workspace_base
from jobs import job_manager
from resilience import PerIPRateLimiter
from database import engine, Base, get_db
from models import Project, TranscriptSegment, JobRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from fastapi import Depends
from vlm_cache import vlm_cache
from auth import get_current_user, create_access_token, get_password_hash, verify_password, get_user_by_email, ACCESS_TOKEN_EXPIRE_MINUTES, revoke_token, initialize_admin_from_env
from models import User
from datetime import timedelta
import jwt

# Initialize logging
log_level = logging.DEBUG if os.getenv("DEBUG_VLM") == "true" else logging.INFO
json_logging = os.getenv("JSON_LOGS", "true").lower() == "true"
setup_logging(log_level=log_level, json_format=json_logging)
logger = get_logger(__name__)

active_projects = set()

# Module-level singletons for VLM engines (preserves circuit breaker state across requests)
_engine: VLMEngine | None = None
_agent: TechnicalAgent | None = None


def get_engine() -> VLMEngine:
    """Get or create the shared VLMEngine instance."""
    global _engine
    if _engine is None:
        _engine = VLMEngine(
            provider=os.getenv("VLM_PROVIDER", "openai"),
            model=os.getenv("VLM_MODEL", "gpt-4o"),
        )
    return _engine


def get_agent() -> TechnicalAgent:
    """Get or create the shared TechnicalAgent instance."""
    global _agent
    if _agent is None:
        _agent = TechnicalAgent(
            provider=os.getenv("VLM_PROVIDER", "openai"),
            model=os.getenv("VLM_MODEL", "gpt-4o"),
        )
    return _agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Try to initialize admin from environment variables
    async with AsyncSession(engine) as db:
        try:
            await initialize_admin_from_env(db)
        except Exception as e:
            logger.warning(f"Could not initialize admin from env vars: {e}")

    yield
    global _engine, _agent
    for req_dir in active_projects:
        frames_dir = Path(req_dir) / ".unmuted" / "frames"
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)
    job_manager.shutdown()
    _engine = None
    _agent = None

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

def get_cors_origins():
    """Build CORS origins list, auto-detecting Render deployments."""
    explicit = os.getenv("CORS_ORIGINS")
    if explicit:
        return [o.strip() for o in explicit.split(",") if o.strip()]

    origins = ["http://localhost:5173", "http://localhost:3000"]

    # Auto-detect Render deployments: add the frontend service URL
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)

    return origins

cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Accept-Ranges", "Content-Range", "Content-Length", "Content-Type"],
)

_per_ip_limiter = PerIPRateLimiter(
    max_calls=int(os.getenv("RATE_LIMIT_MAX_CALLS", "60")),
    time_window=float(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)
        # Exempt job polling from rate limiting
        if request.url.path.startswith("/api/jobs/") and request.method == "GET":
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        if not _per_ip_limiter.allow_request(ip):
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "throttled": True},
                headers={"X-Throttled": "true"},
            )
        return await call_next(request)


app.add_middleware(RateLimitMiddleware)

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


# Authentication Endpoints
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/api/auth/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if this is the first user
    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar()
    
    is_first_user = user_count == 0
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, 
        hashed_password=hashed_password,
        is_approved=is_first_user,
        is_admin=is_first_user
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    if not is_first_user:
        return {"message": "Registration successful. Your account is pending approval by an administrator."}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_admin": db_user.is_admin}

@app.post("/api/auth/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not db_user.is_approved:
        raise HTTPException(status_code=403, detail="Your account is pending approval by an administrator.")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_admin": db_user.is_admin}

@app.post("/api/auth/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    """Revoke the current JWT token."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            from auth import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                revoke_token(jti, exp)
        except Exception:
            pass
    return {"success": True}

@app.get("/api/auth/status")
async def auth_status(db: AsyncSession = Depends(get_db)):
    """Check if the system needs initial setup."""
    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar()
    return {"initialized": user_count > 0}

@app.post("/api/auth/setup")
async def setup_initial_admin(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Initialize the first admin user. Only works if no users exist."""
    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar()

    if user_count > 0:
        raise HTTPException(status_code=403, detail="System is already initialized")

    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password required")

    hashed_password = get_password_hash(user.password)
    admin_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_approved=True,
        is_admin=True
    )
    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_admin": True}

@app.get("/api/auth/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "is_admin": current_user.is_admin}

@app.get("/api/projects")
async def list_projects(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all projects in the database."""
    result = await db.execute(select(Project).where(Project.owner_id == current_user.id).order_by(Project.created_at.desc()))
    projects = result.scalars().all()
    return [{"id": p.id, "title": p.title, "status": p.status, "directory_path": p.directory_path} for p in projects]

# --- Admin Endpoints ---

@app.get("/api/admin/users")
async def list_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "is_approved": u.is_approved, "is_admin": u.is_admin, "created_at": u.created_at} for u in users]

@app.post("/api/admin/users/{user_id}/approve")
async def approve_user(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_approved = True
    await db.commit()
    return {"success": True}

@app.post("/api/admin/users/{user_id}/promote-admin")
async def promote_admin(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own admin status")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    await db.commit()
    return {"success": True}

@app.post("/api/admin/users/{user_id}/demote-admin")
async def demote_admin(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own admin status")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = False
    await db.commit()
    return {"success": True}

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    return {"success": True}

@app.get("/api/cache/stats")
def get_cache_stats():
    """Return VLM response cache statistics."""
    return vlm_cache.stats()

class ScanRequest(BaseModel):
    """Request to scan a directory for video files."""
    directory_path: str
    interval: int = Field(default=3, ge=1)

@app.post("/api/project/scan")
def scan_project(req: ScanRequest, current_user: User = Depends(get_current_user)):
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
        validate_workspace_path(req.directory_path)
        videos = scan_directory_for_videos(req.directory_path)
        return {"videos": videos}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Internal server error")

@app.post("/api/project/upload")
async def upload_video(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Upload a video file to create a new project workspace.

    Args:
        file: Video file (must be video/* content-type, max size configurable)

    Returns:
        dict with success status, absolute workspace directory path, and filename
    """
    try:
        content_type = file.content_type or ""
        if not content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Only video files are accepted")

        safe_filename = Path(file.filename).name
        if not safe_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        workspace_id = str(uuid.uuid4())
        workspace_dir = get_workspace_base() / workspace_id
        workspace_dir.mkdir(parents=True, exist_ok=True)

        video_path = workspace_dir / safe_filename
        max_upload_bytes = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500")) * 1024 * 1024
        total = 0

        with open(video_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > max_upload_bytes:
                    buffer.close()
                    video_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File too large")
                buffer.write(chunk)

        project = Project(
            id=workspace_id,
            title=safe_filename,
            directory_path=str(workspace_dir.absolute()),
            video_filename=safe_filename,
            status="setup",
            owner_id=current_user.id
        )
        db.add(project)
        await db.commit()

        return {
            "success": True,
            "directory_path": str(workspace_dir.absolute()),
            "video_filename": safe_filename,
            "project_id": workspace_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/project/video")
def get_video(directory_path: str, request: Request):
    """
    Stream a video file from the workspace.

    Args:
        directory_path: Workspace directory path

    Returns:
        FileResponse with video file (mp4/webm) and accept-ranges headers
    """
    validate_workspace_path(directory_path)
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
    interval: int = Field(default=3, ge=1)

class FrameRequest(BaseModel):
    directory_path: str
    prompt: str = Field(default="", max_length=2000)
    context: str = Field(default="", max_length=4000)
    frame_index: int
    history: List[str]
    fps: float
    story_plan: List[str] = []
    use_rag: bool = False
    rag_max_frames: int = Field(default=3, ge=1, le=20)
    generate_overlay: bool = True
    synopsis: str = Field(default="", max_length=4000)
    tools_context: str = Field(default="", max_length=4000)

class AutoFinishRequest(BaseModel):
    directory_path: str
    prompt: str = Field(default="", max_length=2000)
    context: str = Field(default="", max_length=4000)
    start_frame_index: int
    history: List[str]
    fps: float
    current_transcript: List[Dict[str, Any]]
    story_plan: List[str] = []
    use_rag: bool = False
    rag_max_frames: int = Field(default=3, ge=1, le=20)
    generate_overlay: bool = True
    synopsis: str = Field(default="", max_length=4000)
    tools_context: str = Field(default="", max_length=4000)

class PlanRequest(BaseModel):
    directory_path: str
    prompt: str = Field(default="", max_length=2000)
    context: str = Field(default="", max_length=4000)
    tool_context: str = Field(default="", max_length=4000)

class SynopsisRequest(BaseModel):
    story_plan: List[str]
    prompt: str = ""
    tool_context: str = ""

class ToolsRequest(BaseModel):
    directory_path: str

@app.post("/api/project/identify-tools")
def identify_tools(req: ToolsRequest, current_user: User = Depends(get_current_user)):
    """
    Identify tools and technologies visible in video keyframes using VLM.

    Uses a multi-image vision analysis to detect tools (Claude Code, Docker, Python, etc.)
    and optionally enriches with web search for unfamiliar technologies.

    Args:
        req: ToolsRequest with directory_path to keyframes

    Returns:
        dict with tools list and rich tool_context string for downstream use
    """
    try:
        validate_workspace_path(req.directory_path)
        planning_frames_dir = os.path.join(req.directory_path, ".unmuted", "plan_frames")
        if not os.path.exists(planning_frames_dir):
            return {"success": True, "tools": [], "tool_context": ""}

        frames = sorted([f for f in os.listdir(planning_frames_dir) if f.endswith(".jpg")])
        if not frames:
            return {"success": True, "tools": [], "tool_context": ""}

        provider = os.getenv("VLM_PROVIDER", "openai")
        model = os.getenv("VLM_MODEL", "gpt-4o")

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
async def generate_plan(req: PlanRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generate a high-level strategic plan for video narration.

    Extracts keyframes, analyzes them with the VLM to understand the video flow,
    and generates a one-sentence-per-phase story plan. Users can review and edit
    the plan before proceeding to frame-by-frame processing.

    Args:
        req: PlanRequest with directory_path, prompt, context, tool_context

    Returns:
        dict with success status and plan list (one sentence per phase)
    """
    try:
        validate_workspace_path(req.directory_path)
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

        logger.info("Extracting keyframes", extra={
            "total_duration_sec": total_duration,
            "target_frames": target_frames,
            "fps": plan_fps
        })

        start_idx = 1
        for i, video in enumerate(videos):
            clear_dir = (i == 0)
            extracted_count = extract_keyframes(video, planning_frames_dir, fps=plan_fps, clear=clear_dir, start_idx=start_idx)
            start_idx += extracted_count

        agent = get_agent()

        logger.info("Calling story plan agent")
        result = agent.generate_story_plan(req.directory_path, req.prompt, req.context, req.tool_context)

        plan = result.get("plan", [])
        logger.info(f"Story plan generated with {len(plan)} phases", extra={"phase_count": len(plan)})

        # Update project in DB
        result = await db.execute(select(Project).where(Project.directory_path == req.directory_path))
        project = result.scalar_one_or_none()
        if project:
            project.prompt = req.prompt
            project.context = req.context
            project.tool_context = req.tool_context
            project.story_plan = plan
            project.status = "planning"
            await db.commit()

        return {"success": True, "plan": plan}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}", extra={"error_type": type(e).__name__}, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/project/synopsises")
def generate_synopsises(req: SynopsisRequest, current_user: User = Depends(get_current_user)):
    """
    Generate 3 distinct narrative synopsises for the video.

    Each synopsis is one sentence emphasizing a different perspective:
    technical outcome, tools used, or problem solved. User selects one
    to guide the frame-by-frame analysis.

    Args:
        req: SynopsisRequest with story_plan, prompt, tool_context

    Returns:
        dict with success status and synopsises list (3 one-sentence strings)
    """
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating synopsises: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/project/frame_image")
def get_frame_image(directory_path: str, frame_index: int):
    """
    Retrieve a specific frame image from the extracted frames.

    Waits up to 30 seconds for the frame to be extracted and written to disk.
    Used during frame-by-frame review to display the current frame.

    Args:
        directory_path: Workspace directory path
        frame_index: Zero-indexed frame number

    Returns:
        FileResponse with JPEG image (frame_XXXX.jpg format)
    """
    validate_workspace_path(directory_path)
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
async def extract_project(req: ExtractRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
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
        validate_workspace_path(req.directory_path)
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

        # Update project in DB
        result = await db.execute(select(Project).where(Project.directory_path == req.directory_path))
        project = result.scalar_one_or_none()
        if project:
            project.total_frames = expected_frames
            project.fps = fps
            project.status = "extracting"
            await db.commit()

        return {
            "success": True,
            "total_frames": expected_frames,
            "fps": fps
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/project/frame_candidates")
def frame_candidates(req: FrameRequest, current_user: User = Depends(get_current_user)):
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
        validate_workspace_path(req.directory_path)
        engine = get_engine()

        result = engine.generate_frame_candidates(req.directory_path, req.frame_index, req.prompt, req.context, req.history, fps=req.fps, story_plan=req.story_plan, use_rag=req.use_rag, rag_max_frames=req.rag_max_frames, generate_overlay=req.generate_overlay, synopsis=req.synopsis, tools_context=req.tools_context)
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating frame candidates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def _run_auto_finish(job, req: AutoFinishRequest) -> dict:
    """Run auto_finish workflow in background with progress tracking."""
    frames_dir = os.path.join(req.directory_path, ".unmuted", "frames")
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(".jpg")])
    total = len(frames)

    engine = get_engine()
    agent = get_agent()

    logger.info(f"auto_finish: starting at frame {req.start_frame_index}, total frames: {total}")

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

    final_state = initial_state
    for step in graph.stream(initial_state):
        if job.is_cancelled():
            raise RuntimeError("Job cancelled by client")
        for node_state in step.values():
            if "idx" in node_state and total > 0:
                job.progress = min(99, int(node_state["idx"] / total * 100))
            final_state = node_state

    logger.info(f"auto_finish: completed, final transcript length: {len(final_state['transcript'])}")
    return {"success": True, "transcript": final_state["transcript"]}


@app.post("/api/project/auto_finish")
async def auto_finish_project(req: AutoFinishRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Submit a long-running auto-finish job for remaining frames.

    Returns immediately with a job_id. The backend processes all remaining frames
    using the LangGraph reflexive critic loop, returning progress via
    /api/jobs/{job_id}/status polling endpoint.

    Args:
        req: AutoFinishRequest with directory_path, story_plan, synopsis, etc.

    Returns:
        dict with success status and job_id for progress polling
    """
    try:
        validate_workspace_path(req.directory_path)
        
        # Get project_id from directory_path
        res = await db.execute(select(Project.id).where(Project.directory_path == req.directory_path))
        project_id = res.scalar_one_or_none()

        job = job_manager.create_job()
        
        # Create JobRecord in DB
        db_job = JobRecord(
            id=job.job_id,
            project_id=project_id,
            status="pending",
            progress=0
        )
        db.add(db_job)
        await db.commit()

        await job_manager.submit(job, _run_auto_finish, req)
        return {"success": True, "job_id": job.job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting auto_finish job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

class OptimizeRequest(BaseModel):
    transcript: List[Dict[str, Any]]

@app.get("/api/jobs/{job_id}/status")
def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    """Get status and progress of a long-running job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    response = {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
    }
    if job.status == "complete":
        response["result"] = job.result
    if job.status == "failed":
        response["error"] = "Job failed"
    return response


@app.delete("/api/jobs/{job_id}")
def cancel_job(job_id: str, current_user: User = Depends(get_current_user)):
    """Cancel a pending or running job."""
    if not job_manager.cancel_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found or not cancellable")
    return {"success": True}


@app.post("/api/project/optimize")
def optimize_project(req: OptimizeRequest, current_user: User = Depends(get_current_user)):
    """
    Optimize and refine the final transcript using LLM.

    Runs the completed transcript through an optimization pass to improve
    clarity, consistency, and narrative flow.

    Args:
        req: OptimizeRequest with transcript (list of narration objects)

    Returns:
        dict with success status and optimized transcript
    """
    try:
        engine = get_engine()

        optimized = engine.optimize_transcript(req.transcript)
        return {"success": True, "transcript": optimized}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing transcript: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

class SaveRequest(BaseModel):
    directory_path: str
    transcript: List[Dict[str, Any]]

class SynthesizeRequest(BaseModel):
    directory_path: str
    voice: str = Field(default="", max_length=100)

def _run_synthesize(job, req: SynthesizeRequest) -> dict:
    """Background worker: generate TTS clips and assemble into timed MP3."""
    import shutil
    from tts import generate_speech, assemble_narration, pick_provider
    from extractor import get_video_duration

    unmuted_dir = Path(req.directory_path) / ".unmuted"
    transcript_path = unmuted_dir / "transcript.json"

    if not transcript_path.exists():
        raise RuntimeError("transcript.json not found; save the transcript first")

    with open(transcript_path) as f:
        data = json.load(f)
    segments = data.get("transcript", [])
    if not segments:
        raise RuntimeError("Transcript is empty")

    # Detect video file for duration
    project_dir = Path(req.directory_path)
    video_files = [
        f for f in project_dir.iterdir()
        if f.is_file() and f.suffix.lower() in {'.mp4', '.mkv', '.mov', '.avi', '.webm'}
    ]
    if not video_files:
        raise RuntimeError("No video file found in project directory")
    video_duration_s = get_video_duration(str(video_files[0]))
    video_duration_ms = int(video_duration_s * 1000)

    # Provider / voice selection
    provider, default_voice = pick_provider()
    voice = req.voice or default_voice

    # Temp directory scoped to this job
    tmp_dir = unmuted_dir / f"tts_tmp_{job.job_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        clip_paths = []
        for i, seg in enumerate(segments):
            if job.is_cancelled():
                raise RuntimeError("Job cancelled")
            text = seg.get("narration", "").strip()
            if not text:
                clip_paths.append(None)
                continue
            clip_path = str(tmp_dir / f"seg_{i:04d}.mp3")
            generate_speech(text, clip_path, provider, voice)
            clip_paths.append(clip_path)
            job.progress = min(80, int((i + 1) / len(segments) * 80))

        output_path = str(unmuted_dir / "narration.mp3")
        assemble_narration(segments, video_duration_ms, clip_paths, output_path)
        job.progress = 99

        return {"success": True, "output": "narration.mp3"}
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)

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
async def save_project(req: SaveRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Save the final transcript and clean up temporary frame files.

    Writes transcript.json and transcript.vtt to the workspace's .unmuted folder.
    Removes temporary frame directories since processing is complete.

    Args:
        req: SaveRequest with directory_path and transcript

    Returns:
        dict with success status
    """
    try:
        validate_workspace_path(req.directory_path)
        unmuted_dir = os.path.join(req.directory_path, ".unmuted")
        os.makedirs(unmuted_dir, exist_ok=True)

        json_path = os.path.join(unmuted_dir, "transcript.json")
        with open(json_path, "w") as f:
            json.dump({"transcript": req.transcript}, f, indent=2)

        vtt_path = os.path.join(unmuted_dir, "transcript.vtt")
        with open(vtt_path, "w") as f:
            f.write(generate_vtt(req.transcript))

        # Update project and segments in DB
        result = await db.execute(select(Project).where(Project.directory_path == req.directory_path))
        project = result.scalar_one_or_none()
        if project:
            project.status = "done"
            
            # Delete existing segments
            await db.execute(delete(TranscriptSegment).where(TranscriptSegment.project_id == project.id))
            
            # Add new segments
            for i, item in enumerate(req.transcript):
                segment = TranscriptSegment(
                    project_id=project.id,
                    timestamp=item["timestamp"],
                    narration=item.get("narration"),
                    overlay=item.get("overlay"),
                    order=i
                )
                db.add(segment)
            
            await db.commit()

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/project/synthesize")
async def synthesize_voiceover(
    req: SynthesizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a background TTS synthesis job.

    Reads transcript.json from the project's .unmuted directory, generates
    speech for each narration segment, and assembles a single timed MP3 file
    (.unmuted/narration.mp3) where each clip starts at its transcript timestamp.

    Args:
        req: SynthesizeRequest with directory_path and optional voice override.

    Returns:
        {"success": true, "job_id": "<uuid>"}
    """
    try:
        validate_workspace_path(req.directory_path)

        res = await db.execute(
            select(Project.id).where(Project.directory_path == req.directory_path)
        )
        project_id = res.scalar_one_or_none()

        job = job_manager.create_job()

        db_job = JobRecord(
            id=job.job_id,
            project_id=project_id,
            status="pending",
            progress=0,
        )
        db.add(db_job)
        await db.commit()

        await job_manager.submit(job, _run_synthesize, req)
        return {"success": True, "job_id": job.job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting synthesize job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/project/download/{file_type}")
def download_artifact(directory_path: str, file_type: str):
    """
    Download a final transcript artifact in the requested format.

    Args:
        directory_path: Workspace directory path
        file_type: Format to download - "json", "vtt", "chapters", or "audio"
            - json: Complete transcript as JSON array of narration objects
            - vtt: WebVTT subtitle format for video editing
            - chapters: YouTube chapter format (HH:MM:SS - Title per line)
            - audio: Synthesized voiceover MP3 file with timed narration

    Returns:
        FileResponse with the requested artifact file
    """
    validate_workspace_path(directory_path)
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
    elif file_type == "audio":
        file_path = unmuted_dir / "narration.mp3"
        media_type = "audio/mpeg"
        filename = "narration.mp3"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
        
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return FileResponse(str(file_path), media_type=media_type, filename=filename)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return generic error."""
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}",
        exc_info=exc,
        extra={"path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )
