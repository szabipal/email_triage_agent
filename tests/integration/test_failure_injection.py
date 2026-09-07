from datetime import UTC, datetime
from pathlib import Path

import pytest

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.calendar import (
    FakeCalendarAdapter,
    decide_proposal,
    execute_approved_proposal,
)
from email_agent.config import Settings
from email_agent.domain import (
    ApprovalDecision,
    CalendarProposalStatus,
    Email,
    EmailIdentity,
    EmailSource,
)
from email_agent.orchestration import triage_email, triage_inbox
from email_agent.persistence import make_session_factory
from email_agent.persistence.models import Base
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository
from email_agent.preprocessing import normalize_email


def settings(tmp_path: Path) -> Settings:
    return Settings(
        **{"_env_file": None, "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}"}
    )


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


def test_malformed_llm_output_does_not_stop_batch(tmp_path: Path) -> None:
    valid = email()
    invalid = email().model_copy(
        update={"id": "email-2", "provider_message_id": "provider-2"}
    )
    processed = normalize_email(valid)
    provider = FakeLLMProvider(
        {
            render_analysis_prompt(processed, output_language="en"): {
                "id": "signals-email-1"
            }
        }
    )
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])

    with session_factory.begin() as session:
        results = triage_inbox(
            [invalid, valid],
            SqlAlchemyRepository(session),
            AnalysisService(provider),
        )

    assert [bool(result.errors) for result in results] == [True, True]


def test_calendar_failure_persists_failed_status(tmp_path: Path) -> None:
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        result = triage_email(email(), repository, meeting_service())
        proposal = result.calendar_proposals[0]
        proposal, approval = decide_proposal(
            proposal,
            ApprovalDecision.APPROVED,
            decided_by="user",
            now=datetime(2026, 1, 2, tzinfo=UTC),
        )
        repository.save_proposal(proposal)
        repository.save_approval(approval)
        with pytest.raises(RuntimeError):
            execute_approved_proposal(
                proposal.id,
                repository,
                FakeCalendarAdapter(fail_proposal_ids={proposal.id}),
            )

    with session_factory() as session:
        saved = SqlAlchemyRepository(session).get_proposal(proposal.id)

    assert saved is not None
    assert saved.status == CalendarProposalStatus.FAILED


def meeting_service() -> AnalysisService:
    item = normalize_email(email())
    return AnalysisService(
        FakeLLMProvider(
            {
                render_analysis_prompt(item, output_language="en"): {
                    "id": "signals-email-1",
                    "processed_email_id": item.id,
                    "summary": "Meeting.",
                    "category": "meeting",
                    "action_required": True,
                    "low_value_type": None,
                    "confidence": 0.9,
                    "meeting_details": [
                        {
                            "title": "Planning",
                            "start_at": "2026-01-02T14:00:00Z",
                        }
                    ],
                }
            }
        )
    )
