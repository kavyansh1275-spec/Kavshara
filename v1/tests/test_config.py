import os
import unittest

from v1.config.settings import Settings


class TestSettings(unittest.TestCase):
    def test_defaults(self) -> None:
        settings = Settings.from_env()
        self.assertEqual(settings.llm_provider, "ollama")
        self.assertTrue(settings.model)
        settings.validate()

    def test_invalid_temperature_is_rejected(self) -> None:
        settings = Settings(temperature=3.0)
        with self.assertRaises(ValueError):
            settings.validate()


if __name__ == "__main__":
    unittest.main()
