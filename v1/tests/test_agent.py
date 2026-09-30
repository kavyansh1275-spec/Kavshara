import unittest

from v1.conversation.manager import ConversationManager
from v1.core.agent import KavsharaAgent
from v1.core.types import Message
from v1.llm.base import LLMProvider


class FakeLLM(LLMProvider):
    def chat(self, messages: list[Message]) -> str:
        self.seen_messages = messages
        return "Test response"


class TestKavsharaAgent(unittest.TestCase):
    def test_agent_handles_message(self) -> None:
        llm = FakeLLM()
        agent = KavsharaAgent(llm, ConversationManager())

        response = agent.handle("Hello Kavshara")

        self.assertEqual(response.content, "Test response")
        self.assertEqual(len(agent.conversation), 3)
        self.assertEqual(agent.conversation.messages()[-1].role, "assistant")

    def test_agent_rolls_back_user_message_on_llm_error(self) -> None:
        class FailingLLM(LLMProvider):
            def chat(self, messages: list[Message]) -> str:
                raise RuntimeError("boom")

        agent = KavsharaAgent(FailingLLM(), ConversationManager())

        with self.assertRaises(RuntimeError):
            agent.handle("Hello")

        self.assertEqual(len(agent.conversation), 1)
        self.assertEqual(agent.conversation.messages()[0].role, "system")


if __name__ == "__main__":
    unittest.main()
