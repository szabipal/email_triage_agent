from datetime import UTC, datetime

from email_agent.domain import Email, EmailIdentity, EmailSource, ProcessedEmailStatus
from email_agent.preprocessing import normalize_email


def make_email(body_raw: str, subject: str = " Hello ") -> Email:
    return Email(
        id="email-1",
        provider_message_id="provider-1",
        subject=subject,
        sender=EmailIdentity(email="ada@example.com"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 2, tzinfo=UTC),
        body_raw=body_raw,
        source=EmailSource.FIXTURE,
    )


def test_normalize_email_converts_html_body_to_text() -> None:
    processed = normalize_email(make_email("<p>Hello <strong>there</strong>.</p>"))

    assert processed.status == ProcessedEmailStatus.PROCESSED
    assert processed.normalized_subject == "Hello"
    assert processed.normalized_body == "Hello there ."
    assert processed.email_id == "email-1"
