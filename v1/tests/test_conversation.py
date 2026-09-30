from v1.conversation.manager import ConversationManager
from v1.core.types import Message


def test_conversation_add_and_clear() -> None:
    conversation = ConversationManager()
    conversation.add(Message("user", "hello"))
    conversation.add(Message("assistant", "hi"))
    assert len(conversation) == 2
    assert conversation.messages()[0].content == "hello"
    conversation.clear()
    assert len(conversation) == 0
