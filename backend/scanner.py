from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.mov', '.avi', '.webm'}

def scan_directory_for_videos(directory_path: str) -> list[str]:
    """Scans the given directory for video files and returns a sorted list of absolute paths."""
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Directory {directory_path} does not exist or is not a directory.")
        
    videos = []
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(str(file.absolute()))
            
    # Sort alphabetically/chronologically
    videos.sort()
    return videos
