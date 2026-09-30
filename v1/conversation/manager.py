"""In-memory conversation history for V1."""

from __future__ import annotations

from typing import List

from ..core.types import Message


class ConversationManager:
    def __init__(self) -> None:
        self._messages: List[Message] = []

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def messages(self) -> List[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def remove_last(self) -> Message | None:
        return self._messages.pop() if self._messages else None

    def __len__(self) -> int:
        return len(self._messages)
