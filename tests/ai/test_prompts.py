from datetime import UTC, datetime

from email_agent.ai.prompts import (
    ANALYSIS_SCHEMA_VERSION,
    ANALYSIS_VERSION,
    render_analysis_prompt,
)
from email_agent.domain import ProcessedEmail, ProcessedEmailStatus


def test_analysis_prompt_has_stable_version_and_schema_metadata() -> None:
    assert ANALYSIS_VERSION == "analysis-v1"
    assert ANALYSIS_SCHEMA_VERSION == "signals-v1"


def test_analysis_prompt_includes_email_and_language_context() -> None:
    processed = ProcessedEmail(
        id="processed-1",
        email_id="email-1",
        normalized_subject="Kérlek",
        normalized_body="Szia, kérlek nézd át.",
        processed_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=ProcessedEmailStatus.PROCESSED,
        detected_language="hu",
    )

    prompt = render_analysis_prompt(processed, output_language="en")

    assert "EmailAnalysisSignals" in prompt
    assert "Source language: hu" in prompt
    assert "Output language: en" in prompt
    assert "Szia, kérlek nézd át." in prompt
