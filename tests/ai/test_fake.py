import pytest

from email_agent.ai import FakeLLMProvider, LLMError, LLMRequest


def request(prompt: str = "prompt") -> LLMRequest:
    return LLMRequest(
        prompt=prompt,
        schema_name="signals-v1",
        prompt_version="analysis-v1",
        model="fake-llm",
    )


def test_fake_llm_returns_configured_structured_output() -> None:
    provider = FakeLLMProvider({"prompt": {"summary": "Configured."}})

    response = provider.complete_structured(request())

    assert response.output == {"summary": "Configured."}
    assert response.model_name == "fake-llm"
    assert provider.requests == [request()]


def test_fake_llm_can_raise_configured_error() -> None:
    provider = FakeLLMProvider({"prompt": {}}, errors={"prompt"})

    with pytest.raises(LLMError, match="fake LLM error"):
        provider.complete_structured(request())
