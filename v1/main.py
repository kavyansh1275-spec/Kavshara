"""Kavshara V1 entry point.

main.py deliberately contains no intelligence or command-specific logic.
"""

from __future__ import annotations

import logging

from .config.settings import Settings
from .core.agent import KavsharaAgent
from .conversation.manager import ConversationManager
from .llm.ollama import OllamaError, OllamaProvider
from .utils.logging import configure_logging

logger = logging.getLogger(__name__)


def build_agent(settings: Settings) -> KavsharaAgent:
    settings.validate()
    llm = OllamaProvider(settings)
    conversation = ConversationManager()
    return KavsharaAgent(llm, conversation)


def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    logger.info("Starting %s V1", settings.app_name)

    try:
        agent = build_agent(settings)
    except Exception as exc:
        logger.exception("Kavshara could not start")
        print(f"Startup error: {exc}")
        return

    print("Kavshara V1 ready. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKavshara: Bye! 👋")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Kavshara: Bye! 👋")
            break
        if not user_input:
            continue

        try:
            response = agent.handle(user_input)
            print(f"Kavshara: {response.content}")
        except OllamaError as exc:
            logger.error("LLM error: %s", exc)
            print(f"Kavshara: I couldn't reach Ollama right now. {exc}")
        except Exception:
            logger.exception("Unexpected request failure")
            print("Kavshara: Something went wrong while processing that request.")


if __name__ == "__main__":
    main()
