from datetime import UTC, datetime
from pathlib import Path

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.config import Settings
from email_agent.domain import (
    CalendarProposalStatus,
    DeadlineCandidate,
    Email,
    EmailAnalysisStatus,
    EmailIdentity,
    EmailSource,
    MeetingCandidate,
    PriorityBand,
)
from email_agent.orchestration import triage_email, triage_inbox
from email_agent.persistence import make_session_factory
from email_agent.persistence.models import Base
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository
from email_agent.preprocessing import normalize_email
from email_agent.retrieval import ChromaIndex, FakeEmbeddingProvider, index_processed_email


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


def test_batch_triage_isolates_malformed_email_failure(tmp_path: Path) -> None:
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    valid = email()
    invalid = email().model_copy(
        update={"id": "email-2", "provider_message_id": "provider-2", "body_raw": ""}
    )

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        results = triage_inbox([invalid, valid], repository, fake_service(valid))

    assert results[0].errors == ["email body is empty"]
    assert results[1].analysis is not None


def test_triage_uses_retrieved_context_before_analysis(tmp_path: Path) -> None:
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    provider = FakeEmbeddingProvider()
    index = ChromaIndex(tmp_path / "chroma")
    source = email().model_copy(
        update={
            "id": "email-source",
            "provider_message_id": "provider-source",
            "subject": "Invoice background",
            "body_raw": "Legal approved the vendor exception.",
        }
    )
    current = email().model_copy(
        update={
            "id": "email-current",
            "provider_message_id": "provider-current",
            "subject": "Invoice approval",
            "body_raw": "Can you approve the invoice?",
        }
    )
    source_processed = normalize_email(source)
    index_processed_email(source_processed, provider, index)
    current_processed = normalize_email(current)
    prompt = render_analysis_prompt(
        current_processed,
        output_language="en",
        context=[f"{source_processed.normalized_subject}\n{source_processed.normalized_body}"],
    )
    analysis_service = AnalysisService(
        FakeLLMProvider(
            {
                prompt: {
                    "id": "signals-current",
                    "processed_email_id": current_processed.id,
                    "summary": "Context shows legal approved the exception.",
                    "category": "finance",
                    "action_required": True,
                    "low_value_type": None,
                    "confidence": 0.9,
                }
            }
        )
    )

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        result = triage_email(
            current,
            repository,
            analysis_service,
            embedding_provider=provider,
            index=index,
        )

    assert result.retrieved_context[0].source_email_ids == ["email-source"]
    assert result.signals is not None
    assert result.signals.summary.startswith("Context shows")


def test_triage_creates_calendar_proposal_from_meeting_signal(tmp_path: Path) -> None:
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    email_ = email().model_copy(update={"body_raw": "Let's meet tomorrow."})
    processed = normalize_email(email_)
    prompt = render_analysis_prompt(processed, output_language="en")
    analysis_service = AnalysisService(
        FakeLLMProvider(
            {
                prompt: {
                    "id": "signals-email-1",
                    "processed_email_id": processed.id,
                    "summary": "Ada proposes a meeting.",
                    "category": "meeting",
                    "action_required": True,
                    "low_value_type": None,
                    "confidence": 0.9,
                    "meeting_details": [
                        MeetingCandidate(
                            title="Review",
                            start_at=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
                        ).model_dump(mode="json")
                    ],
                }
            }
        )
    )

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        result = triage_email(email_, repository, analysis_service)

    assert result.calendar_proposals[0].status == CalendarProposalStatus.PENDING
    assert result.analysis is not None
    assert result.analysis.calendar_proposal_ids == ["proposal-email-1-meeting-1"]


def test_triage_creates_incomplete_proposal_from_ambiguous_deadline(
    tmp_path: Path,
) -> None:
    session_factory = make_session_factory(settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    email_ = email().model_copy(update={"body_raw": "Please finish soon."})
    processed = normalize_email(email_)
    prompt = render_analysis_prompt(processed, output_language="en")
    analysis_service = AnalysisService(
        FakeLLMProvider(
            {
                prompt: {
                    "id": "signals-email-1",
                    "processed_email_id": processed.id,
                    "summary": "Ada asks for work soon.",
                    "category": "work",
                    "action_required": True,
                    "low_value_type": None,
                    "confidence": 0.9,
                    "deadlines": [
                        DeadlineCandidate(
                            description="Finish soon",
                            uncertainty="soon is not a concrete date",
                        ).model_dump(mode="json")
                    ],
                }
            }
        )
    )

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        result = triage_email(email_, repository, analysis_service)

    assert result.calendar_proposals[0].status == CalendarProposalStatus.INCOMPLETE
    assert result.calendar_proposals[0].missing_fields == ["start_at"]
