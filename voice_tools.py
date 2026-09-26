import os
import subprocess
import tempfile
from pathlib import Path

from config import MODEL
from ai_provider import OllamaProvider

VOICE_DIR = Path("data/voice")
VOICE_DIR.mkdir(parents=True, exist_ok=True)


def speak(text):
    text = str(text).strip()
    if not text:
        return {"error": "text is empty."}
    try:
        escaped = text.replace("'", "''")
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Add-Type -AssemblyName System.Speech; "
            f"$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Speak('{escaped}')"
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "stderr": result.stderr[:4000],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "failed", "error": str(exc)}


def voice_status():
    return {
        "speech_output": "Windows System.Speech",
        "local_model": MODEL,
        "voice_input": "SpeechRecognition + Google en-IN recognition",
        "note": "Microphone input is explicit and foreground-only; continuous listening is never started automatically.",
    }


def build_voice_tools(registry):
    registry.register(
        "speak",
        "Speak text aloud using Windows built-in speech synthesis. Argument: text.",
        speak,
    )
    registry.register(
        "voice_status",
        "Show Kavshara voice capability status.",
        voice_status,
    )
    return registry
