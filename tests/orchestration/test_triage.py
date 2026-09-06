from datetime import UTC, datetime
from pathlib import Path

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.config import Settings
from email_agent.domain import (
    Email,
    EmailAnalysisStatus,
    EmailIdentity,
    EmailSource,
    PriorityBand,
)
from email_agent.orchestration import triage_email
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


def fake_service(email_: Email) -> AnalysisService:
    processed = normalize_email(email_)
    prompt = render_analysis_prompt(processed, output_language="en")
    return AnalysisService(
        FakeLLMProvider(
            {
                prompt: {
                    "id": "signals-email-1",
                    "processed_email_id": processed.id,
                    "summary": "Ada asks for review today.",
                    "category": "work",
                    "action_required": True,
                    "low_value_type": None,
                    "confidence": 0.9,
                }
            }
        )
    )


def test_single_email_triage_persists_analysis_with_fake_services(tmp_path: Path) -> None:
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    email_ = email()

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        result = triage_email(email_, repository, fake_service(email_))

    with session_factory() as session:
        repository = SqlAlchemyRepository(session)
        saved = repository.get_analysis("analysis-email-1")

    assert result.analysis is not None
    assert result.analysis.status == EmailAnalysisStatus.COMPLETED
    assert result.priority_result is not None
    assert result.priority_result.band == PriorityBand.HIGH
    assert saved is not None
