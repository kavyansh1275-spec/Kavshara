"""Centralized configuration for Kavshara V1."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Kavshara"
    llm_provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    model: str = "qwen2.5:3b"
    temperature: float = 0.7
    request_timeout: float = 120.0
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("KAVSHARA_APP_NAME", "Kavshara"),
            llm_provider=os.getenv("KAVSHARA_LLM_PROVIDER", "ollama").lower(),
            ollama_url=os.getenv("KAVSHARA_OLLAMA_URL", "http://localhost:11434").rstrip("/"),
            model=os.getenv("KAVSHARA_MODEL", "qwen2.5:3b"),
            temperature=float(os.getenv("KAVSHARA_TEMPERATURE", "0.7")),
            request_timeout=float(os.getenv("KAVSHARA_REQUEST_TIMEOUT", "120")),
            log_level=os.getenv("KAVSHARA_LOG_LEVEL", "INFO").upper(),
        )

    def validate(self) -> None:
        if self.llm_provider != "ollama":
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        if not self.model.strip():
            raise ValueError("KAVSHARA_MODEL cannot be empty")
        if not 0 <= self.temperature <= 2:
            raise ValueError("KAVSHARA_TEMPERATURE must be between 0 and 2")
        if self.request_timeout <= 0:
            raise ValueError("KAVSHARA_REQUEST_TIMEOUT must be greater than 0")
