import queue
import threading
import time

from permissions import get_permissions


class VoiceInterface:
    def __init__(self, brain):
        self.brain = brain
        self.stop_event = threading.Event()
        self.events = queue.Queue()

    def listen_once(self):
        if not get_permissions().get("desktop_access"):
            return {"error": "Desktop access is not granted."}

        try:
            import speech_recognition as sr
        except ImportError:
            return {"error": "Install SpeechRecognition to use microphone input."}

        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Kavshara is listening...")
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)

            text = recognizer.recognize_google(audio, language="en-IN")
            if not text.strip():
                return {"status": "empty"}
            return {"status": "success", "text": text}
        except sr.WaitTimeoutError:
            return {"status": "timeout", "error": "No speech detected."}
        except sr.UnknownValueError:
            return {"status": "failed", "error": "I could not understand that."}
        except sr.RequestError as exc:
            return {"status": "failed", "error": str(exc)}
        except OSError as exc:
            return {"status": "failed", "error": str(exc)}

    def voice_command(self):
        result = self.listen_once()
        if result.get("status") != "success":
            return result

        response = self.brain.respond(result["text"])
        return {"status": "success", "heard": result["text"], "response": response}

    def stop(self):
        self.stop_event.set()

    def run_loop(self, callback=None, interval=0.2):
        if not get_permissions().get("desktop_access"):
            return {"error": "Desktop access is not granted."}

        self.stop_event.clear()
        while not self.stop_event.is_set():
            result = self.voice_command()
            if callback:
                callback(result)
            if result.get("status") == "failed":
                time.sleep(interval)
        return {"status": "stopped"}


def build_voice_interface_tools(registry, brain=None):
    if brain is None:
        return registry

    interface = VoiceInterface(brain)
    registry.register(
        "listen_once",
        "Listen through the default microphone once and return transcribed speech.",
        interface.listen_once,
    )
    registry.register(
        "voice_command",
        "Listen once, send the recognized speech to Kavshara, and return its response.",
        interface.voice_command,
    )
    return registry
