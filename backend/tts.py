import os
from pathlib import Path


def _timestamp_to_ms(ts: str) -> int:
    ts = ts.split(".")[0]
    parts = ts.split(":")
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    return (h * 3600 + m * 60 + s) * 1000


def pick_provider() -> tuple[str, str]:
    if os.getenv("ELEVENLABS_API_KEY"):
        return ("elevenlabs", "Rachel")
    return ("openai", "alloy")


def generate_speech(text: str, output_path: str, provider: str, voice: str) -> str:
    if provider == "openai":
        return _generate_openai(text, output_path, voice)
    elif provider == "elevenlabs":
        return _generate_elevenlabs(text, output_path, voice)
    raise ValueError(f"Unknown provider: {provider}")


def _generate_openai(text, output_path, voice):
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3"
    )
    Path(output_path).write_bytes(response.content)
    return output_path


def _generate_elevenlabs(text, output_path, voice):
    from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    audio = client.text_to_speech.convert(voice_id=voice, text=text)
    Path(output_path).write_bytes(b"".join(audio))
    return output_path


def assemble_narration(segments, video_duration_ms, clip_paths, output_path):
    """Assemble narration clips into a timed MP3 using ffmpeg."""
    import subprocess
    import tempfile
    from pathlib import Path

    # Create a temporary directory for the concat file
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Build ffmpeg concat demuxer file
        concat_file = Path(tmp_dir) / "concat.txt"
        concat_lines = []

        for i, (seg, clip_path) in enumerate(zip(segments, clip_paths)):
            if clip_path is None:
                continue

            start_ms = _timestamp_to_ms(seg["timestamp"])
            next_ms = (
                _timestamp_to_ms(segments[i + 1]["timestamp"])
                if i + 1 < len(segments)
                else video_duration_ms
            )
            window_ms = next_ms - start_ms

            # Get clip duration
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1:noprint_wrappers=1",
                    clip_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            clip_duration_sec = float(result.stdout.strip())
            clip_duration_ms = int(clip_duration_sec * 1000)

            # Trim clip if it exceeds the window
            trimmed_path = clip_path
            if window_ms > 0 and clip_duration_ms > window_ms:
                window_sec = window_ms / 1000.0
                trimmed_path = Path(tmp_dir) / f"trimmed_{i}.mp3"
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        clip_path,
                        "-t",
                        str(window_sec),
                        "-q:a",
                        "9",
                        str(trimmed_path),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )

            concat_lines.append(f"file '{trimmed_path}'")

        # Write concat file
        concat_file.write_text("\n".join(concat_lines))

        # Use ffmpeg to concatenate clips
        if concat_lines:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat_file),
                    "-c",
                    "copy",
                    output_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        else:
            # If no clips, create silent MP3
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=44100:cl=mono",
                    "-t",
                    str(video_duration_ms / 1000.0),
                    "-q:a",
                    "9",
                    output_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

    return output_path
