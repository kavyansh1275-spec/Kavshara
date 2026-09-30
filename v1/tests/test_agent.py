from v1.core.agent import KavsharaAgent
from v1.conversation.manager import ConversationManager
from v1.core.types import Message
from v1.llm.base import LLMProvider


class FakeLLM(LLMProvider):
    def chat(self, messages: list[Message]) -> str:
        assert messages[-1].role == "user"
        return "Test response"


def test_agent_handles_message() -> None:
    agent = KavsharaAgent(FakeLLM(), ConversationManager())
    response = agent.handle("Hello Kavshara")
    assert response.content == "Test response"
