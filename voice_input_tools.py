import json
import subprocess
import tempfile
from pathlib import Path

from permissions import get_permissions

VOICE_DIR = Path("data/voice")
VOICE_DIR.mkdir(parents=True, exist_ok=True)


def _require_access():
    if not get_permissions().get("desktop_access"):
        return {"error": "Desktop access is not granted."}
    return None


def transcribe_audio(audio_path):
    denied = _require_access()
    if denied:
        return denied

    path = Path(audio_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        return {"error": "Audio file does not exist."}
    if path.stat().st_size > 25_000_000:
        return {"error": "Audio file is too large."}

    try:
        import speech_recognition as sr
    except ImportError:
        return {
            "error": "Speech recognition dependency is not installed.",
            "install": "pip install SpeechRecognition",
        }

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(str(path)) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="en-IN")
        return {"status": "success", "text": text, "language": "en-IN"}
    except sr.UnknownValueError:
        return {"status": "failed", "error": "Speech could not be understood."}
    except sr.RequestError as exc:
        return {"status": "failed", "error": f"Speech recognition service unavailable: {exc}"}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def voice_input_status():
    try:
        import speech_recognition
        installed = True
    except ImportError:
        installed = False
    return {
        "installed": installed,
        "language": "en-IN",
        "supports_hinglish": "Recognition uses Indian English; Hindi/Hinglish accuracy depends on the recognizer.",
        "microphone_mode": "audio-file transcription foundation",
    }


def build_voice_input_tools(registry):
    registry.register(
        "transcribe_audio",
        "Transcribe a WAV/AIFF/FLAC audio file using speech recognition. Argument: audio_path.",
        transcribe_audio,
    )
    registry.register(
        "voice_input_status",
        "Show speech-to-text capability status.",
        voice_input_status,
    )
    return registry
