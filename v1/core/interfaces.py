"""Interfaces for future-extensible Kavshara components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from .types import AgentResponse, Message


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: Sequence[Message]) -> str:
        """Generate a response from a conversation."""
        raise NotImplementedError


class Tool(ABC):
    name: str = "unnamed_tool"

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute a future tool action."""
        raise NotImplementedError


class Integration(ABC):
    name: str = "unnamed_integration"

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError


class Memory(ABC):
    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, key: str) -> Any:
        raise NotImplementedError


class Observer(ABC):
    @abstractmethod
    def observe(self) -> Any:
        raise NotImplementedError


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, data: Any) -> Any:
        raise NotImplementedError


class Learner(ABC):
    @abstractmethod
    def learn(self, data: Any) -> None:
        raise NotImplementedError


class Agent(ABC):
    @abstractmethod
    def handle(self, user_input: str) -> AgentResponse:
        raise NotImplementedError
