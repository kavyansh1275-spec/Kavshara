"""Kavshara's V1 reasoning/conversation boundary."""

from __future__ import annotations

import logging

from .interfaces import Agent as AgentInterface, LLMProvider
from .types import AgentResponse, Message
from ..conversation.manager import ConversationManager
from ..personality.system_prompt import KAVSHARA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class KavsharaAgent(AgentInterface):
    def __init__(self, llm: LLMProvider, conversation: ConversationManager) -> None:
        self._llm = llm
        self._conversation = conversation
        self._conversation.add(Message("system", KAVSHARA_SYSTEM_PROMPT))

    def handle(self, user_input: str) -> AgentResponse:
        text = user_input.strip()
        if not text:
            return AgentResponse("Please say something and I'll be here.")

        self._conversation.add(Message("user", text))
        try:
            response = self._llm.chat(self._conversation.messages())
        except Exception:
            logger.exception("Agent request failed")
            # Remove the failed user turn so the in-memory conversation stays consistent.
            self._conversation.remove_last()
            raise

        response_text = response.strip()
        self._conversation.add(Message("assistant", response_text))
        return AgentResponse(response_text)
