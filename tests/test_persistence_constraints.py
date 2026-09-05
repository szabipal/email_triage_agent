from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError

from email_agent.config import Settings
from email_agent.domain import Email, EmailIdentity, EmailSource
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


def make_email(email_id: str, provider_message_id: str) -> Email:
    return Email(
        id=email_id,
        provider_message_id=provider_message_id,
        subject="Review",
        sender=EmailIdentity(email="ada@example.com"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 2, tzinfo=UTC),
        body_raw="Please review.",
        source=EmailSource.FIXTURE,
    )


def test_duplicate_provider_message_id_is_rejected(tmp_path: Path) -> None:
    session_factory = make_session_factory(build_settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])

    with pytest.raises(IntegrityError):
        with session_factory.begin() as session:
            repository = SqlAlchemyRepository(session)
            repository.save_email(make_email("email-1", "provider-1"))
            repository.save_email(make_email("email-2", "provider-1"))
