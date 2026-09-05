from pathlib import Path
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EMAIL_AGENT_",
        extra="ignore",
    )

    environment: Literal["development", "test", "demo"] = "development"
    database_url: str = "sqlite:///./data/email_agent.db"
    vector_store_path: Path = Path("./data/chroma")

    llm_provider: Literal["fake", "openai"] = "fake"
    llm_model: str = "fake-llm"
    llm_api_key: SecretStr | None = None

    embedding_provider: Literal["fake", "openai"] = "fake"
    embedding_model: str = "fake-embedding"
    embedding_dimension: int = Field(default=8, gt=0)
    embedding_api_key: SecretStr | None = None

    calendar_provider: Literal["fake", "google"] = "fake"
    calendar_execution_enabled: bool = False
    google_calendar_credentials_path: Path | None = None

    output_language: str = "en"
    locale: str = "en_US"
    timezone: str = "UTC"

    feature_flags: dict[str, bool] = Field(default_factory=dict)
    priority_weights: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_provider_credentials(self) -> Self:
        if self.llm_provider != "fake" and self.llm_api_key is None:
            raise ValueError(
                "EMAIL_AGENT_LLM_API_KEY is required for real LLM providers"
            )

        if self.embedding_provider != "fake" and self.embedding_api_key is None:
            raise ValueError(
                "EMAIL_AGENT_EMBEDDING_API_KEY is required for real embedding providers"
            )

        if (
            self.calendar_execution_enabled
            and self.calendar_provider == "google"
            and self.google_calendar_credentials_path is None
        ):
            raise ValueError(
                "EMAIL_AGENT_GOOGLE_CALENDAR_CREDENTIALS_PATH is required for "
                "Google Calendar execution"
            )

        return self


def load_settings() -> Settings:
    return Settings()
