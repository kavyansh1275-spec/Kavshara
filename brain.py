from ai_provider import OllamaProvider
from memory import Memory
from tools import ToolRegistry


class Brain:
    def __init__(self, provider=None, memory=None, tools=None):
        self.provider = provider or OllamaProvider()
        self.memory = memory or Memory()
        self.tools = tools or ToolRegistry()

    def respond(self, user_message: str) -> str:
        text = user_message.strip()
        if not text:
            return "Tell me what you want me to do."

        # V1 deliberately keeps tool execution separate from free-form chat.
        # Tool routing will be added here as skills are implemented.
        return self.provider.ask(text, self.memory.context())

    def remember(self, text: str):
        self.memory.add(text, kind="user_memory")
        return "Saved to memory."

    def status(self):
        return {
            "model": self.provider.model,
            "ollama": self.provider.is_available(),
            "tools": self.tools.names(),
            "memory_items": len(self.memory.items),
        }
