from datetime import UTC, datetime

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.domain import EmailAnalysisSignals, ProcessedEmail, ProcessedEmailStatus


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
