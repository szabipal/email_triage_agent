from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from email_agent.domain import Email, EmailIdentity, EmailSource, PriorityBand
from email_agent.evaluation import DatasetSplit, EvaluationLabels, FixtureRecord


def test_fixture_record_validates_domain_email_and_labels() -> None:
    record = FixtureRecord(
        id="fixture-1",
        split=DatasetSplit.DEV,
        scenario_ids=["action"],
        email=Email(
            id="email-1",
            provider_message_id="fixture-email-1",
            subject="Review request",
            sender=EmailIdentity(email="ada@example.com"),
            recipients=[EmailIdentity(email="user@example.com")],
            received_at=datetime(2026, 1, 2, 9, tzinfo=UTC),
            body_raw="Please review this today.",
            source=EmailSource.FIXTURE,
        ),
        labels=EvaluationLabels(
            summary="Ada asks for review today.",
            category="work",
            action_required=True,
            priority_band=PriorityBand.HIGH,
        ),
    )

    assert FixtureRecord.model_validate_json(record.model_dump_json()) == record


def test_fixture_record_rejects_current_email_as_related_source() -> None:
    with pytest.raises(ValidationError, match="exclude current email"):
        FixtureRecord(
            id="fixture-1",
            split=DatasetSplit.DEV,
            scenario_ids=["context"],
            email=Email(
                id="email-1",
                provider_message_id="fixture-email-1",
                subject="Review request",
                sender=EmailIdentity(email="ada@example.com"),
                recipients=[EmailIdentity(email="user@example.com")],
                received_at=datetime(2026, 1, 2, 9, tzinfo=UTC),
                body_raw="Following up on this.",
                source=EmailSource.FIXTURE,
            ),
            labels=EvaluationLabels(
                category="work",
                action_required=True,
                priority_band=PriorityBand.HIGH,
                expected_related_source_email_ids=["email-1"],
                retrieval_should_run=True,
            ),
        )
