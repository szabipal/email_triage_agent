from __future__ import annotations

from email_agent.ai.fake import FakeLLMProvider
from email_agent.ai.provider import LLMProvider
from email_agent.ai.real import OpenAILLMProvider
from email_agent.config import Settings


def make_llm_provider(
    settings: Settings,
    *,
    fake_outputs: dict[str, dict[str, object]] | None = None,
) -> LLMProvider:
    if settings.llm_provider == "openai":
        assert settings.llm_api_key is not None
        return OpenAILLMProvider(settings.llm_api_key.get_secret_value())
    return FakeLLMProvider(fake_outputs or {})
