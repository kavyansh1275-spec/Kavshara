import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from brain import Brain
from permissions import get_permissions, request_desktop_access
from voice_interface import VoiceInterface


class KavsharaDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kavshara")
        self.root.geometry("900x650")
        self.brain = Brain()
        self.voice = VoiceInterface(self.brain)
        self._build()

    def _build(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=12, pady=10)
        tk.Label(top, text="Kavshara", font=("Segoe UI", 20, "bold")).pack(side="left")
        self.status = tk.Label(top, text=self._status_text())
        self.status.pack(side="right")

        self.chat = scrolledtext.ScrolledText(self.root, wrap="word", state="disabled", font=("Segoe UI", 11))
        self.chat.pack(fill="both", expand=True, padx=12, pady=6)

        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", padx=12, pady=10)
        self.entry = tk.Entry(bottom, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda _event: self.send())
        tk.Button(bottom, text="Send", command=self.send).pack(side="left", padx=5)
        tk.Button(bottom, text="🎤 Voice", command=self.voice_once).pack(side="left")

        actions = tk.Frame(self.root)
        actions.pack(fill="x", padx=12, pady=(0, 10))
        tk.Button(actions, text="Desktop Access", command=self.request_access).pack(side="left")
        tk.Button(actions, text="Refresh Status", command=self.refresh_status).pack(side="left", padx=5)
        tk.Button(actions, text="Clear", command=self.clear).pack(side="right")

        self._append("Kavshara", "Ready. Ask me to research, code, work with approved files, or open an application.")

    def _status_text(self):
        perms = get_permissions()
        desktop = "Desktop: ON" if perms.get("desktop_access") else "Desktop: OFF"
        ollama = "Ollama: ON" if self.brain.provider.is_available() else "Ollama: OFF"
        return f"{desktop} | {ollama}"

    def _append(self, speaker, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{speaker}: {text}\n\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def refresh_status(self):
        self.status.configure(text=self._status_text())

    def request_access(self):
        result = request_desktop_access()
        self._append("Kavshara", result["status"].capitalize() + " desktop access.")
        self.refresh_status()

    def clear(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")

    def send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._append("You", text)
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()

    def _respond(self, text):
        try:
            answer = self.brain.respond(text)
        except Exception as exc:
            answer = f"Error: {exc}"
        self.root.after(0, lambda: self._append("Kavshara", answer))

    def voice_once(self):
        self._append("Kavshara", "Listening...")
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self):
        result = self.voice.voice_command(speak_response=True)
        if result.get("status") == "success":
            self.root.after(0, lambda: self._append("You (voice)", result["heard"]))
            self.root.after(0, lambda: self._append("Kavshara", result["response"]))
        else:
            self.root.after(0, lambda: self._append("Kavshara", result.get("error", "Voice input failed.")))


def main():
    root = tk.Tk()
    app = KavsharaDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
