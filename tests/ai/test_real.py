import json
from email.message import Message
from urllib.error import HTTPError

from email_agent.ai import (
    FakeLLMProvider,
    LLMRequest,
    OpenAILLMProvider,
    make_llm_provider,
)
from email_agent.config import Settings


class Response:
    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def read(self) -> bytes:
        return json.dumps(
            {
                "output_text": json.dumps({"summary": "ok"}),
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "total_tokens": 15,
                },
            }
        ).encode()


def test_openai_adapter_posts_structured_responses_request(monkeypatch) -> None:
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return Response()

    monkeypatch.setattr("email_agent.ai.real.urlrequest.urlopen", fake_urlopen)

    response = OpenAILLMProvider("test-key").complete_structured(
        LLMRequest(
            prompt="Analyze.",
            schema_name="signals-v1",
            prompt_version="analysis-v1",
            model="gpt-5",
            timeout_seconds=3,
            json_schema={"type": "object"},
        )
    )

    posted = json.loads(calls[0][0].data)
    assert calls[0][1] == 3
    assert posted["text"]["format"]["type"] == "json_schema"
    assert posted["text"]["format"]["schema"] == {"type": "object"}
    assert response.output == {"summary": "ok"}
    assert response.input_tokens == 10
    assert response.output_tokens == 5
    assert response.total_tokens == 15


def test_llm_provider_factory_uses_settings() -> None:
    fake = make_llm_provider(Settings(**{"_env_file": None, "llm_provider": "fake"}))
    real = make_llm_provider(
        Settings(
            **{
                "_env_file": None,
                "llm_provider": "openai",
                "llm_model": "gpt-5",
                "llm_api_key": "test-key",
            }
        )
    )

    assert isinstance(fake, FakeLLMProvider)
    assert isinstance(real, OpenAILLMProvider)


def test_openai_adapter_maps_rate_limit_errors(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        raise HTTPError(
            url="https://api.openai.test",
            code=429,
            msg="too many",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("email_agent.ai.real.urlrequest.urlopen", fake_urlopen)

    try:
        OpenAILLMProvider("test-key").complete_structured(
            LLMRequest(
                prompt="Analyze.",
                schema_name="signals-v1",
                prompt_version="analysis-v1",
                model="gpt-5",
                json_schema={"type": "object"},
            )
        )
    except Exception as error:
        assert type(error).__name__ == "LLMError"
        assert str(error) == "rate_limited"
    else:
        raise AssertionError("expected rate limit error")
