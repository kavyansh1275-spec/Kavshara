from agent import Agent
from ai_provider import OllamaProvider
from memory import Memory
from specialist_tools.registry import build_specialist_registry


class Brain:
    def __init__(self, provider=None, memory=None, tools=None, executor=None):
        self.provider = provider or OllamaProvider()
        self.memory = memory or Memory()

        if tools is None or executor is None:
            self.tools, self.executor = build_specialist_registry()
        else:
            self.tools = tools
            self.executor = executor

        self.agent = Agent(
            self.provider,
            self.tools,
            self.executor,
            self.memory,
        )

    def respond(self, user_message):
        text = user_message.strip()
        if not text:
            return "Tell me what you want me to do."

        answer = self.agent.run(text)
        self.memory.add(f"User: {text}\nKavshara: {answer}", kind="conversation")
        return answer

    def remember(self, text):
        self.memory.add(text, kind="user_memory")
        return "Saved to memory."

    def status(self):
        return {
            "model": self.provider.model,
            "ollama": self.provider.is_available(),
            "tools": self.tools.names(),
            "tool_metadata": self.tools.metadata(),
            "memory_items": len(self.memory.items),
        }
