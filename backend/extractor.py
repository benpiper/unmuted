import subprocess
import asyncio
import json
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

def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace(":", "\\:")
    return text

def _ts_to_seconds(ts: str) -> float:
    parts = ts.strip().split(':')
    return sum(float(v) * m for v, m in zip(reversed(parts), [1, 60, 3600]))

def _hex_to_ffmpeg(color: str) -> str:
    if color.startswith('#'):
        return '0x' + color[1:].upper()
    return color

def render_mp4(
    video_path: str,
    output_path: str,
    segments: list,
    font_path: str,
    caption_color: str = "white",
    overlay_color: str = "white",
    caption_fontsize: int = 28,
    overlay_fontsize: int = 32,
    caption_position: str = "bottom",
) -> None:
    video_duration = get_video_duration(video_path)

    drawtext_filters = []

    for i, seg in enumerate(segments):
        start = _ts_to_seconds(seg['timestamp'])
        end = _ts_to_seconds(segments[i + 1]['timestamp']) if i + 1 < len(segments) else video_duration

        narration = seg.get('narration', '').strip()
        overlay = seg.get('overlay', '').strip()

        if narration:
            escaped_narration = _escape_drawtext(narration)
            if caption_position == 'bottom':
                caption_y = 'h-text_h-30'
            elif caption_position == 'middle':
                caption_y = '(h-text_h)/2'
            else:  # top
                caption_y = '80'
            drawtext = (
                f"drawtext=fontfile={font_path}:text={escaped_narration}:fontcolor={_hex_to_ffmpeg(caption_color)}:"
                f"fontsize={caption_fontsize}:x=(w-text_w)/2:y={caption_y}:"
                f"box=1:boxcolor=black@0.5:boxborderw=8:enable=between(t\\,{start}\\,{end})"
            )
            drawtext_filters.append(drawtext)

        if overlay:
            escaped_overlay = _escape_drawtext(overlay)
            drawtext = (
                f"drawtext=fontfile={font_path}:text={escaped_overlay}:fontcolor={_hex_to_ffmpeg(overlay_color)}:"
                f"fontsize={overlay_fontsize}:x=(w-text_w)/2:y=20:"
                f"box=1:boxcolor=black@0.5:boxborderw=8:enable=between(t\\,{start}\\,{end})"
            )
            drawtext_filters.append(drawtext)

    command = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
    ]

    if drawtext_filters:
        command.extend([
            "-vf", ",".join(drawtext_filters),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "copy",
        ])
    else:
        command.extend([
            "-c:v", "copy",
            "-c:a", "copy",
        ])

    command.append(str(output_path))

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed: {e.stderr.decode()}")
