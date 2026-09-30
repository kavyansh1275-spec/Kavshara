"""Minimal Ollama HTTP provider using only the Python standard library."""

from __future__ import annotations

import json
import logging
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config.settings import Settings
from ..core.interfaces import LLMProvider
from ..core.types import Message

logger = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    """Raised when Ollama cannot complete a request."""


class OllamaProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_url
        self.model = settings.model
        self.temperature = settings.temperature
        self.timeout = settings.request_timeout

    def chat(self, messages: Sequence[Message]) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        logger.info("Sending request to Ollama model=%s", self.model)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(f"Ollama HTTP {exc.code}: {details[:500]}") from exc
        except URLError as exc:
            raise OllamaError(
                "Could not connect to Ollama. Make sure Ollama is running."
            ) from exc
        except TimeoutError as exc:
            raise OllamaError("Ollama request timed out.") from exc

        try:
            data = json.loads(raw)
            content = data["message"]["content"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise OllamaError("Ollama returned an invalid response.") from exc

        if not isinstance(content, str) or not content.strip():
            raise OllamaError("Ollama returned an empty response.")
        return content
