import subprocess
import asyncio
from pathlib import Path

async def async_get_video_duration(video_path: str) -> float:
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", video_path
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode()}")
    return float(stdout.decode().strip())

def get_video_duration(video_path: str) -> float:
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def extract_keyframes(video_path: str, output_dir: str, fps: float = 1.0, clear: bool = True, start_idx: int = 1) -> int:
    """
    Extracts keyframes from a video file. Returns the number of frames extracted.
    """
    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    out_dir_obj = Path(output_dir)
    out_dir_obj.mkdir(parents=True, exist_ok=True)
    
    if clear:
        for file in out_dir_obj.iterdir():
            if file.is_file() and file.name.startswith("frame_"):
                file.unlink()
            
    output_pattern = str(out_dir_obj / "frame_%04d.jpg")
    
    # Run ffmpeg to extract frames
    command = [
        "ffmpeg",
        "-y", # overwrite output files
        "-i", str(video_path_obj.absolute()),
        "-vf", f"fps={fps},scale='min(1920,iw)':-1", # downscale to 1080p if larger
        "-start_number", str(start_idx),
        "-q:v", "5", # Good quality JPEG, smaller size
        output_pattern
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed to extract frames from {video_path}: {e}")
        
    # Return count of frames
    count = 0
    for file in out_dir_obj.iterdir():
        if file.is_file() and file.name.startswith("frame_"):
            count += 1
            
    return count
