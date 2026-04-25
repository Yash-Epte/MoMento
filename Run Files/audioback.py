import argparse
import json
import os
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


ELEVENLABS_API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io")


def transcribe_file(
    audio_path: str,
    *,
    api_key: str,
    model_id: str = "scribe_v2",
    language_code: str | None = None,
    diarize: bool = False,
    timestamps_granularity: str = "word",  # none|word|character
    tag_audio_events: bool = True,
) -> dict:
    url = f"{ELEVENLABS_API_BASE}/v1/speech-to-text"
    headers = {"xi-api-key": api_key}

    data: dict[str, str] = {
        "model_id": model_id,
        "timestamps_granularity": timestamps_granularity,
        "diarize": str(diarize).lower(),
        "tag_audio_events": str(tag_audio_events).lower(),
    }
    if language_code:
        data["language_code"] = language_code

    audio_path = str(Path(audio_path))
    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f)}
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=300)
        resp.raise_for_status()
        return resp.json()


def main() -> None:
    p = argparse.ArgumentParser(description="Transcribe audio/video with ElevenLabs Speech-to-Text.")
    p.add_argument("audio_path", help="Path to an audio/video file (mp3, wav, mp4, etc.)")
    p.add_argument("--out-json", help="Optional path to save full JSON response")
    p.add_argument("--model-id", default="scribe_v2", choices=["scribe_v2", "scribe_v1"])
    p.add_argument("--language-code", default=None, help="Optional ISO-639-1/3 hint, e.g. en, es, ka")
    p.add_argument("--diarize", action="store_true", help="Enable speaker diarization")
    p.add_argument("--timestamps", default="word", choices=["none", "word", "character"])
    args = p.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ELEVENLABS_API_KEY environment variable.")

    result = transcribe_file(
        args.audio_path,
        api_key=api_key,
        model_id=args.model_id,
        language_code=args.language_code,
        diarize=args.diarize,
        timestamps_granularity=args.timestamps,
    )

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(result.get("text", json.dumps(result, ensure_ascii=False, indent=2)))


if __name__ == "__main__":
    main()
import argparse
import json
import os
from pathlib import Path

import requests


try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()

ELEVENLABS_API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io")


def transcribe_file(
    audio_path: str,
    *,
    api_key: str,
    model_id: str = "scribe_v2",
    language_code: str | None = None,
    diarize: bool = False,
    timestamps_granularity: str = "word",  # none|word|character
    tag_audio_events: bool = True,
) -> dict:
    url = f"{ELEVENLABS_API_BASE}/v1/speech-to-text"
    headers = {"xi-api-key": api_key}

    data: dict[str, str] = {
        "model_id": model_id,
        "timestamps_granularity": timestamps_granularity,
        "diarize": str(diarize).lower(),
        "tag_audio_events": str(tag_audio_events).lower(),
    }
    if language_code:
        data["language_code"] = language_code

    audio_path = str(Path(audio_path))
    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f)}
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=300)
        resp.raise_for_status()
        return resp.json()


def main() -> None:
    p = argparse.ArgumentParser(description="Transcribe audio/video with ElevenLabs Speech-to-Text.")
    p.add_argument("audio_path", help="Path to an audio/video file (mp3, wav, mp4, etc.)")
    p.add_argument("--out-json", help="Optional path to save full JSON response")
    p.add_argument("--model-id", default="scribe_v2", choices=["scribe_v2", "scribe_v1"])
    p.add_argument("--language-code", default=None, help="Optional ISO-639-1/3 hint, e.g. en, es, ka")
    p.add_argument("--diarize", action="store_true", help="Enable speaker diarization")
    p.add_argument("--timestamps", default="word", choices=["none", "word", "character"])
    args = p.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ELEVENLABS_API_KEY environment variable.")

    result = transcribe_file(
        args.audio_path,
        api_key=api_key,
        model_id=args.model_id,
        language_code=args.language_code,
        diarize=args.diarize,
        timestamps_granularity=args.timestamps,
    )

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(result.get("text", json.dumps(result, ensure_ascii=False, indent=2)))


if __name__ == "__main__":
    main()
