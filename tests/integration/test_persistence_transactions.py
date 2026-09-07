from datetime import UTC, datetime
from pathlib import Path

import pytest

from email_agent.config import Settings
from email_agent.domain import Email, EmailIdentity, EmailSource
from email_agent.persistence import make_session_factory
from email_agent.persistence.database import session_scope
from email_agent.persistence.models import Base
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository


def build_settings(tmp_path: Path) -> Settings:
    return Settings(
        **{
            "_env_file": None,
            "database_url": f"sqlite:///{tmp_path / 'email_agent.db'}",
        }
    )


def test_transaction_rolls_back_partial_email_write(tmp_path: Path) -> None:
    session_factory = make_session_factory(build_settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])

    with pytest.raises(RuntimeError, match="boom"):
        with session_scope(session_factory) as session:
            SqlAlchemyRepository(session).save_email(
                Email(
                    id="email-rollback",
                    provider_message_id="provider-rollback",
                    subject="Rollback",
                    sender=EmailIdentity(email="ada@example.com"),
                    recipients=[EmailIdentity(email="user@example.com")],
                    received_at=datetime(2026, 1, 2, tzinfo=UTC),
                    body_raw="This should roll back.",
                    source=EmailSource.FIXTURE,
                )
            )
            raise RuntimeError("boom")

    with session_factory() as session:
        assert SqlAlchemyRepository(session).get_email("email-rollback") is None
