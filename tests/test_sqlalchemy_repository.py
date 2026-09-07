from datetime import UTC, datetime
from pathlib import Path

from email_agent.config import Settings
from email_agent.domain import (
    Email,
    EmailAnalysis,
    EmailAnalysisSignals,
    EmailAnalysisStatus,
    EmailIdentity,
    EmailSource,
    PriorityBand,
    PriorityFactor,
    PriorityFactorDirection,
    PriorityResult,
    ProcessedEmail,
    ProcessedEmailStatus,
)
from email_agent.persistence import make_session_factory
from email_agent.persistence.models import Base
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository


def build_settings(tmp_path: Path) -> Settings:
    return Settings(
        **{
            "_env_file": None,
            "database_url": f"sqlite:///{tmp_path / 'email_agent.db'}",
        }
    )


def test_repository_persists_email_and_analysis_across_sessions(tmp_path: Path) -> None:
    session_factory = make_session_factory(build_settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    now = datetime(2026, 1, 2, tzinfo=UTC)

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        repository.save_email(
            Email(
                id="email-1",
                provider_message_id="provider-1",
                subject="Review",
                sender=EmailIdentity(email="ada@example.com"),
                recipients=[EmailIdentity(email="user@example.com")],
                received_at=now,
                body_raw="Please review.",
                source=EmailSource.FIXTURE,
            )
        )
        repository.save_processed_email(
            ProcessedEmail(
                id="processed-1",
                email_id="email-1",
                normalized_subject="review",
                normalized_body="Please review.",
                processed_at=now,
                status=ProcessedEmailStatus.PROCESSED,
            )
        )
        repository.save_signals(
            EmailAnalysisSignals(
                id="signals-1",
                processed_email_id="processed-1",
                summary="Ada asks for review.",
                category="work",
                action_required=True,
                low_value_type=None,
                confidence=0.9,
            )
        )
        repository.save_priority_result(
            PriorityResult(
                id="priority-1",
                email_id="email-1",
                score=80,
                band=PriorityBand.HIGH,
                factors=[
                    PriorityFactor(
                        name="action required",
                        direction=PriorityFactorDirection.POSITIVE,
                        weight=1,
                    )
                ],
                calculated_at=now,
                ruleset_version="priority-v1",
            )
        )
        repository.save_analysis(
            EmailAnalysis(
                id="analysis-1",
                email_id="email-1",
                processed_email_id="processed-1",
                signals_id="signals-1",
                priority_result_id="priority-1",
                status=EmailAnalysisStatus.COMPLETED,
            )
        )

    with session_factory() as session:
        repository = SqlAlchemyRepository(session)

        assert repository.get_email("email-1") is not None
        assert repository.get_analysis("analysis-1") is not None
