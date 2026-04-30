import subprocess
import asyncio
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

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

async def async_extract_keyframes_parallel(video_path: str, output_dir: str, fps: float = 1.0, clear: bool = True, start_idx: int = 1, chunks: int = 4) -> int:
    """
    Extracts keyframes from a video file in parallel using time-based chunking.
    Returns the total number of frames extracted.
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

    duration = await async_get_video_duration(video_path)
    if duration <= 0:
        return 0

    chunk_duration = duration / chunks
    
    import tempfile
    import shutil
    
    # We need a shared temp root to avoid cross-device link errors when moving
    temp_root = out_dir_obj / ".tmp_extraction"
    temp_root.mkdir(parents=True, exist_ok=True)

    temp_dirs = []
    tasks = []

    for i in range(chunks):
        chunk_start = i * chunk_duration
        tdir = tempfile.mkdtemp(dir=temp_root)
        temp_dirs.append(tdir)
        
        output_pattern = str(Path(tdir) / "frame_%04d.jpg")
        
        command = [
            "ffmpeg",
            "-y",
            "-ss", str(chunk_start),
            "-t", str(chunk_duration),
            "-i", str(video_path_obj.absolute()),
            "-vf", f"fps={fps},scale='min(1920,iw)':-1",
            "-q:v", "5",
            output_pattern
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        tasks.append(process.wait())
        
    # Wait for all chunks to extract in parallel
    await asyncio.gather(*tasks)
    
    # Gather all extracted files, sorted by chunk, then by frame number
    all_extracted_files = []
    for tdir in temp_dirs:
        chunk_files = sorted([f for f in Path(tdir).iterdir() if f.is_file() and f.name.endswith('.jpg')])
        all_extracted_files.extend(chunk_files)
        
    # Move and rename sequentially
    current_idx = start_idx
    for file_path in all_extracted_files:
        dest_path = out_dir_obj / f"frame_{current_idx:04d}.jpg"
        shutil.move(str(file_path), str(dest_path))
        current_idx += 1
        
    # Cleanup temp dirs
    shutil.rmtree(str(temp_root), ignore_errors=True)
    
    return current_idx - start_idx

def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace(":", "\\:")
    text = text.replace(",", "\\,")
    return text

def _ts_to_seconds(ts: str) -> float:
    parts = ts.strip().split(':')
    return sum(float(v) * m for v, m in zip(reversed(parts), [1, 60, 3600]))

def _hex_to_ffmpeg(color: str) -> str:
    if color.startswith('#'):
        return '0x' + color[1:].upper()
    return color

def _wrap_text(text: str, max_width: int = 70) -> str:
    """Wrap text to max_width characters per line, breaking at word boundaries."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= max_width:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)

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

    with tempfile.TemporaryDirectory() as tmpdir:
        drawtext_filters = []

        for i, seg in enumerate(segments):
            start = _ts_to_seconds(seg['timestamp'])
            end = _ts_to_seconds(segments[i + 1]['timestamp']) if i + 1 < len(segments) else video_duration

            narration = seg.get('narration', '').strip()
            overlay = seg.get('overlay', '').strip()

            if narration:
                textfile = str(Path(tmpdir) / f"seg_{i:04d}_narration.txt")
                wrapped_narration = _wrap_text(narration)
                Path(textfile).write_text(wrapped_narration, encoding='utf-8')
                if caption_position == 'bottom':
                    caption_y = 'h-text_h-30'
                elif caption_position == 'middle':
                    caption_y = '(h-text_h)/2'
                else:
                    caption_y = '80'
                drawtext = (
                    f"drawtext=fontfile={font_path}:textfile={textfile}:fontcolor={_hex_to_ffmpeg(caption_color)}:"
                    f"fontsize={caption_fontsize}:x=(w-text_w)/2:y={caption_y}:"
                    f"box=1:boxcolor=black@0.5:boxborderw=8:enable=between(t\\,{start}\\,{end})"
                )
                drawtext_filters.append(drawtext)

            if overlay:
                textfile = str(Path(tmpdir) / f"seg_{i:04d}_overlay.txt")
                wrapped_overlay = _wrap_text(overlay)
                Path(textfile).write_text(wrapped_overlay, encoding='utf-8')
                drawtext = (
                    f"drawtext=fontfile={font_path}:textfile={textfile}:fontcolor={_hex_to_ffmpeg(overlay_color)}:"
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
        logger.info(f"ffmpeg render command: {' '.join(command)}")

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg failed: {e.stderr.decode()}")
