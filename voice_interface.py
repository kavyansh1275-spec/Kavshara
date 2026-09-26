import speech_recognition as sr

from config import MODEL
from voice_tools import speak


class VoiceInterface:
    """Foreground, push-to-talk voice interface for Kavshara."""

    def __init__(self, brain):
        self.brain = brain

    def listen_once(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Kavshara: Haan, bolo...")
                recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=20)

            # en-IN handles common English/Hindi/Hinglish speech reasonably well.
            text = recognizer.recognize_google(audio, language="en-IN").strip()
            if not text:
                return {"status": "empty"}
            return {"status": "success", "text": text}
        except sr.WaitTimeoutError:
            return {"status": "timeout", "error": "Koi baat nahi, jab ready ho tab bolo."}
        except sr.UnknownValueError:
            return {"status": "failed", "error": "Mujhe properly sunai nahi diya. Ek baar phir bolo."}
        except sr.RequestError as exc:
            return {"status": "failed", "error": f"Speech recognition service error: {exc}"}
        except OSError as exc:
            return {"status": "failed", "error": str(exc)}

    def voice_command(self, speak_response=True):
        result = self.listen_once()
        if result.get("status") != "success":
            return result

        response = self.brain.respond(result["text"])
        spoken = False
        if speak_response:
            spoken = speak(response).get("status") == "success"

        return {
            "status": "success",
            "heard": result["text"],
            "response": response,
            "spoken": spoken,
        }


def voice_status():
    return {
        "speech_input": "SpeechRecognition + Google en-IN",
        "speech_output": "Windows System.Speech",
        "model": MODEL,
        "mode": "foreground push-to-talk",
        "language": "English / Hindi / Hinglish",
    }
