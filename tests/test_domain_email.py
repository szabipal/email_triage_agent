from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from email_agent.domain import (
    Email,
    EmailIdentity,
    EmailSource,
    EmailThread,
)


def test_email_preserves_source_facts_through_json_round_trip() -> None:
    email = Email(
        id="email-1",
        provider_message_id="provider-1",
        subject="Quarterly planning",
        sender=EmailIdentity(email="ada@example.com", display_name="Ada"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
        body_raw="<p>Please review the plan.</p>",
        source=EmailSource.FIXTURE,
        thread_id="thread-1",
        headers={"Message-ID": "<provider-1@example.com>"},
        labels=["inbox"],
    )

    restored = Email.model_validate_json(email.model_dump_json())

    assert restored == email
    assert restored.body_raw == "<p>Please review the plan.</p>"


def test_email_requires_recipient() -> None:
    with pytest.raises(ValidationError, match="recipients"):
        Email(
            id="email-1",
            provider_message_id="provider-1",
            subject="No recipient",
            sender=EmailIdentity(email="ada@example.com"),
            recipients=[],
            received_at=datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
            body_raw="Hello",
            source=EmailSource.FIXTURE,
        )


def test_email_thread_validates_seen_range() -> None:
    with pytest.raises(ValidationError, match="last_seen_at"):
        EmailThread(
            id="thread-1",
            subject_key="quarterly-planning",
            email_ids=["email-1"],
            first_seen_at=datetime(2026, 1, 2, tzinfo=UTC),
            last_seen_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
