import json
from datetime import UTC, datetime
from io import StringIO

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.domain import Email, EmailIdentity, EmailSource
from email_agent.logging import configure_logging
from email_agent.orchestration import triage_email
from email_agent.preprocessing import normalize_email


class Repo:
    def __init__(self) -> None:
        self.preferences = []

    def save_email(self, email): ...

    def save_processed_email(self, processed_email): ...

    def save_signals(self, signals): ...

    def save_priority_result(self, priority_result): ...

    def save_context(self, context): ...

    def save_analysis(self, analysis): ...

    def save_proposal(self, proposal): ...

    def list_preferences(self):
        return self.preferences


def email() -> Email:
    return Email(
        id="email-1",
        provider_message_id="provider-1",
        subject="Review today",
        sender=EmailIdentity(email="ada@example.com"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 1, tzinfo=UTC),
        body_raw="Please review today.",
        source=EmailSource.FIXTURE,
    )


def test_triage_logs_processing_status() -> None:
    stream = StringIO()
    configure_logging(stream=stream)
    item = normalize_email(email())
    service = AnalysisService(
        FakeLLMProvider(
            {
                render_analysis_prompt(item, output_language="en"): {
                    "id": "signals-email-1",
                    "processed_email_id": item.id,
                    "summary": "Ada asks for review today.",
                    "category": "work",
                    "action_required": True,
                    "low_value_type": None,
                    "confidence": 0.9,
                }
            }
        )
    )

    triage_email(email(), Repo(), service)

    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert [event["stage"] for event in events] == ["start", "complete"]
    assert all(event["email_id"] == "email-1" for event in events)
    assert events[-1]["priority_band"] == "high"
