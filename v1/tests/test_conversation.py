import unittest

from v1.conversation.manager import ConversationManager
from v1.core.types import Message


class TestConversationManager(unittest.TestCase):
    def test_conversation_add_and_clear(self) -> None:
        conversation = ConversationManager()
        conversation.add(Message("user", "hello"))
        conversation.add(Message("assistant", "hi"))

        self.assertEqual(len(conversation), 2)
        self.assertEqual(conversation.messages()[0].content, "hello")

        conversation.clear()
        self.assertEqual(len(conversation), 0)


if __name__ == "__main__":
    unittest.main()
