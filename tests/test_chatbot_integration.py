"""Offline chatbot integration tests for Kavshara.

These tests do not require Ollama, a microphone, or Windows voice output.
They verify that the conversational entry point can route a model tool call
through the specialist tool system and then return a final chat response.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain import Brain
from tool_system import ToolExecutor, ToolRegistry


class FakeProvider:
    """Deterministic provider used to test the chat loop without an LLM."""

    model = "test-model"

    def __init__(self):
        self.calls = 0

    def is_available(self):
        return True

    def chat(self, messages):
        self.calls += 1
        if self.calls == 1:
            return '{"type":"tool_call","tool":"calculator","arguments":{"expression":"12 * 8"}}'
        return "12 × 8 = 96. Done."


class FakeMemory:
    def __init__(self):
        self.items = []

    def add(self, content, kind="note"):
        self.items.append({"kind": kind, "content": content})

    def context(self, limit=10):
        return "\n".join(item["content"] for item in self.items[-limit:])


class ChatbotIntegrationTests(unittest.TestCase):
    def test_brain_can_complete_a_tool_call_and_return_chat_response(self):
        provider = FakeProvider()
        memory = FakeMemory()

        # Use the real registry/executor so this tests the production routing path.
        brain = Brain(provider=provider, memory=memory)

        answer = brain.respond("Calculate 12 times 8.")

        self.assertEqual(answer, "12 × 8 = 96. Done.")
        self.assertEqual(provider.calls, 2)
        self.assertEqual(len(memory.items), 1)
        self.assertIn("Calculate 12 times 8.", memory.items[0]["content"])

    def test_empty_message_is_handled_without_calling_model(self):
        provider = FakeProvider()
        brain = Brain(provider=provider, memory=FakeMemory())

        self.assertEqual(
            brain.respond("   "),
            "Tell me what you want me to do.",
        )
        self.assertEqual(provider.calls, 0)

    def test_tool_executor_rejects_unknown_tool(self):
        registry = ToolRegistry()
        executor = ToolExecutor(registry)

        result = executor.execute("does_not_exist", {})

        self.assertEqual(result["status"], "error")
        self.assertIn("Unknown tool", result["error"])

    def test_main_entrypoint_is_importable(self):
        import main  # noqa: F401

        self.assertTrue(callable(main.main))


if __name__ == "__main__":
    unittest.main()
