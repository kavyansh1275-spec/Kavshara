import json
import unittest
from unittest.mock import patch

from v1.config.settings import Settings
from v1.core.types import Message
from v1.llm.ollama import OllamaError, OllamaProvider


class FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class TestOllamaProvider(unittest.TestCase):
    def test_chat_parses_response_and_builds_request(self) -> None:
        settings = Settings(
            ollama_url="http://example.test",
            model="qwen2.5:3b",
            temperature=0.4,
        )
        provider = OllamaProvider(settings)

        with patch(
            "v1.llm.ollama.urlopen",
            return_value=FakeHTTPResponse(
                {"message": {"content": "hello from qwen"}}
            ),
        ) as mocked_urlopen:
            result = provider.chat([Message("user", "hello")])

        self.assertEqual(result, "hello from qwen")
        request = mocked_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://example.test/api/chat")
        self.assertEqual(payload["model"], "qwen2.5:3b")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "hello"}])
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"]["temperature"], 0.4)

    def test_invalid_response_raises_ollama_error(self) -> None:
        provider = OllamaProvider(Settings(ollama_url="http://example.test"))

        with patch(
            "v1.llm.ollama.urlopen",
            return_value=FakeHTTPResponse({"message": {}}),
        ):
            with self.assertRaises(OllamaError):
                provider.chat([Message("user", "hello")])


if __name__ == "__main__":
    unittest.main()
