from v1.config.settings import Settings


def test_defaults() -> None:
    settings = Settings.from_env()
    assert settings.llm_provider == "ollama"
    assert settings.model
    settings.validate()
