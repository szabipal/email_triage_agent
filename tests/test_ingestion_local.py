from pathlib import Path

from email_agent.domain import EmailSource
from email_agent.ingestion import load_fixture_emails


def test_load_fixture_emails_returns_domain_emails() -> None:
    emails = load_fixture_emails(Path("datasets/fixtures/dev.jsonl"))

    assert emails
    assert all(email.source == EmailSource.FIXTURE for email in emails)
    assert any(email.provider_message_id == "fixture-dev-001" for email in emails)
