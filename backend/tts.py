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
    from pydub import AudioSegment
    silent_track = AudioSegment.silent(duration=video_duration_ms)
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
        clip = AudioSegment.from_mp3(clip_path)
        if window_ms > 0 and len(clip) > window_ms:
            clip = clip[:window_ms]
        silent_track = silent_track.overlay(clip, position=start_ms)
    silent_track.export(output_path, format="mp3")
    return output_path
