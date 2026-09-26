import requests
from config import OLLAMA_HOST, MODEL, TEMPERATURE, SYSTEM_PROMPT


class OllamaProvider:
    def __init__(self, host: str = OLLAMA_HOST, model: str = MODEL):
        self.host = host
        self.model = model

    def chat(self, messages):
        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": TEMPERATURE},
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()

    def ask(self, user_message: str, memory_context: str = ""):
        system = SYSTEM_PROMPT
        if memory_context:
            system += f"\n\nRelevant saved memory:\n{memory_context}"
        return self.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ])

    def is_available(self):
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.ok
        except requests.RequestException:
            return False
