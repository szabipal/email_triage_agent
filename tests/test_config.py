import pytest
from pydantic import ValidationError

from email_agent.config import Settings


def build_settings(**values: object) -> Settings:
    return Settings(**{"_env_file": None, **values})


def test_settings_use_fake_safe_defaults() -> None:
    settings = build_settings()

    assert settings.environment == "development"
    assert settings.database_url == "sqlite:///./data/email_agent.db"
    assert settings.vector_store_path.as_posix() == "data/chroma"
    assert settings.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert settings.llm_provider == "fake"
    assert settings.embedding_provider == "fake"
    assert settings.calendar_provider == "fake"
    assert settings.calendar_execution_enabled is False
    assert settings.output_language == "en"
    assert settings.locale == "en_US"
    assert settings.timezone == "UTC"


def test_settings_read_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_AGENT_ENVIRONMENT", "test")
    monkeypatch.setenv("EMAIL_AGENT_DATABASE_URL", "sqlite:///./tmp/test.db")
    monkeypatch.setenv("EMAIL_AGENT_OUTPUT_LANGUAGE", "hu")
    monkeypatch.setenv("EMAIL_AGENT_LOCALE", "hu_HU")
    monkeypatch.setenv("EMAIL_AGENT_TIMEZONE", "Europe/Budapest")
    monkeypatch.setenv("EMAIL_AGENT_ALLOWED_ORIGINS", '["https://demo.example"]')

    settings = build_settings()

    assert settings.environment == "test"
    assert settings.database_url == "sqlite:///./tmp/test.db"
    assert settings.output_language == "hu"
    assert settings.locale == "hu_HU"
    assert settings.timezone == "Europe/Budapest"
    assert settings.allowed_origins == ["https://demo.example"]


def test_real_llm_provider_requires_api_key() -> None:
    with pytest.raises(ValidationError, match="EMAIL_AGENT_LLM_API_KEY"):
        build_settings(llm_provider="openai")


def test_google_calendar_execution_requires_credentials_path() -> None:
    with pytest.raises(
        ValidationError,
        match="EMAIL_AGENT_GOOGLE_CALENDAR_CREDENTIALS_PATH",
    ):
        build_settings(
            calendar_provider="google",
            calendar_execution_enabled=True,
        )
