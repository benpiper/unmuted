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
    """Assemble narration clips into a timed MP3 using ffmpeg with proper positioning."""
    import subprocess
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # First pass: prepare clips (trim if needed)
        prepared_clips = []
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
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1:noprint_wrappers=1",
                    clip_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            clip_duration_ms = int(float(result.stdout.strip()) * 1000)

            # Trim clip if it exceeds the window
            if window_ms > 0 and clip_duration_ms > window_ms:
                window_sec = window_ms / 1000.0
                trimmed_path = tmp_path / f"trimmed_{i}.mp3"
                subprocess.run(
                    [
                        "ffmpeg", "-y",
                        "-i", clip_path,
                        "-t", str(window_sec),
                        "-q:a", "9",
                        str(trimmed_path),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                prepared_clips.append((i, start_ms, trimmed_path))
            else:
                prepared_clips.append((i, start_ms, clip_path))

        # Create silent base track
        silent_path = tmp_path / "silent.mp3"
        duration_sec = video_duration_ms / 1000.0
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"anullsrc=r=44100:cl=mono,atrim=0:{duration_sec}",
                "-q:a", "9",
                str(silent_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        # Overlay each clip at its timestamp using amerge filter
        if prepared_clips:
            # Build ffmpeg filter chain to overlay all clips
            filter_chain_parts = ["[0:a]"]
            input_args = ["-i", str(silent_path)]

            for idx, (i, start_ms, clip_path) in enumerate(prepared_clips):
                input_args.extend(["-i", str(clip_path)])
                # Add delay to position the clip at its start timestamp
                delay_sec = start_ms / 1000.0
                filter_chain_parts.append(
                    f"[{idx + 1}:a]adelay={int(start_ms)}|{int(start_ms)}[delayed_{idx}]"
                )

            # Mix all delayed clips with the silent base
            mix_inputs = "[0:a]"
            for idx in range(len(prepared_clips)):
                mix_inputs += f"[delayed_{idx}]"
            filter_chain_parts.append(f"{mix_inputs}amix=inputs={len(prepared_clips) + 1}:duration=longest[out]")

            filter_chain = ";".join(filter_chain_parts)

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    *input_args,
                    "-filter_complex", filter_chain,
                    "-map", "[out]",
                    "-q:a", "9",
                    output_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        else:
            # No clips, just copy the silent track
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(silent_path),
                    "-c", "copy",
                    output_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

    return output_path
