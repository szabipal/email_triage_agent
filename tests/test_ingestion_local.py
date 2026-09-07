from pathlib import Path

from email_agent.config import Settings
from email_agent.domain import EmailSource
from email_agent.ingestion import import_fixture_emails, load_fixture_emails
from email_agent.persistence import make_session_factory
from email_agent.persistence.models import Base
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository


def build_settings(tmp_path: Path) -> Settings:
    return Settings(
        **{
            "_env_file": None,
            "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}",
        }
    )


def test_load_fixture_emails_returns_domain_emails() -> None:
    emails = load_fixture_emails(Path("datasets/fixtures/dev.jsonl"))

    assert emails
    assert all(email.source == EmailSource.FIXTURE for email in emails)
    assert any(email.provider_message_id == "fixture-dev-001" for email in emails)


def test_import_fixture_emails_skips_duplicates(tmp_path: Path) -> None:
    session_factory = make_session_factory(build_settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)

        first_import = import_fixture_emails(
            Path("datasets/fixtures/dev.jsonl"),
            repository,
        )
        second_import = import_fixture_emails(
            Path("datasets/fixtures/dev.jsonl"),
            repository,
        )

    assert first_import
    assert second_import == []
