import json
from datetime import UTC, datetime
from io import StringIO

from email_agent.ai import (
    AnalysisService,
    FakeLLMProvider,
    LLMError,
    LLMRequest,
    LLMResponse,
)
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.domain import (
    EmailAnalysisSignals,
    ProcessedEmail,
    ProcessedEmailStatus,
)
from email_agent.logging import configure_logging


class SignalRepo:
    def __init__(self) -> None:
        self.saved: list[EmailAnalysisSignals] = []

    def save_signals(self, signals: EmailAnalysisSignals) -> None:
        self.saved.append(signals)


def processed_email() -> ProcessedEmail:
    return ProcessedEmail(
        id="processed-1",
        email_id="email-1",
        normalized_subject="Review",
        normalized_body="Please review today.",
        processed_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=ProcessedEmailStatus.PROCESSED,
        detected_language="en",
    )


def test_analysis_service_validates_and_persists_fake_output() -> None:
    processed = processed_email()
    prompt = render_analysis_prompt(processed, output_language="en")
    provider = FakeLLMProvider(
        {
            prompt: {
                "id": "signals-1",
                "processed_email_id": "processed-1",
                "summary": "The sender asks for a review today.",
                "category": "work",
                "action_required": True,
                "low_value_type": None,
                "confidence": 0.9,
                "source_language": "en",
                "output_language": "en",
            }
        }
    )
    repo = SignalRepo()

    result = AnalysisService(provider).analyze(processed, repo)

    assert result.errors == []
    assert result.signals is not None
    assert result.signals.prompt_version == "analysis-v1"
    assert result.signals.model_name == "fake-llm"
    assert repo.saved == [result.signals]


def test_analysis_service_returns_error_for_invalid_output() -> None:
    processed = processed_email()
    prompt = render_analysis_prompt(processed, output_language="en")
    provider = FakeLLMProvider({prompt: {"id": "signals-1"}})

    result = AnalysisService(provider).analyze(processed)

    assert result.signals is None
    assert result.errors


def test_analysis_service_retries_timeout_and_then_persists() -> None:
    processed = processed_email()
    provider = FlakyProvider()
    repo = SignalRepo()

    result = AnalysisService(provider, max_retries=1).analyze(processed, repo)

    assert result.signals is not None
    assert provider.calls == 2
    assert repo.saved == [result.signals]
    assert result.signals.total_tokens == 12


def test_analysis_service_never_persists_invalid_output() -> None:
    processed = processed_email()
    prompt = render_analysis_prompt(processed, output_language="en")
    repo = SignalRepo()

    result = AnalysisService(
        FakeLLMProvider({prompt: {"id": "signals-1"}}),
        max_retries=1,
    ).analyze(processed, repo)

    assert result.signals is None
    assert repo.saved == []


def test_analysis_service_logs_sanitized_provider_failures() -> None:
    stream = StringIO()
    configure_logging(stream=stream)

    result = AnalysisService(FailingProvider()).analyze(processed_email())

    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert result.errors == ["LLMError"]
    assert events[0]["event"] == "llm analysis failed"
    assert events[0]["error_type"] == "LLMError"
    assert "private prompt" not in stream.getvalue()


class FlakyProvider:
    def __init__(self) -> None:
        self.calls = 0

    def complete_structured(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("timed out")
        return LLMResponse(
            output={
                "id": "signals-1",
                "processed_email_id": "processed-1",
                "summary": "The sender asks for a review today.",
                "category": "work",
                "action_required": True,
                "low_value_type": None,
                "confidence": 0.9,
            },
            model_name=request.model,
            prompt_version=request.prompt_version,
            schema_version=request.schema_name,
            input_tokens=8,
            output_tokens=4,
            total_tokens=12,
        )


class FailingProvider:
    def complete_structured(self, request: LLMRequest) -> LLMResponse:
        raise LLMError("private prompt should not be logged")
