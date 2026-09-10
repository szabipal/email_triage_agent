from pathlib import Path

import pytest

from email_agent.config import Settings
from email_agent.domain import EmailSource
from email_agent.ingestion import (
    import_eml_emails,
    import_fixture_emails,
    load_eml_email,
    load_fixture_emails,
)
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


def test_load_eml_email_parses_basic_message(tmp_path: Path) -> None:
    path = tmp_path / "message.eml"
    path.write_text(
        "Message-ID: <real-1@example.test>\n"
        "Date: Mon, 5 Jan 2026 09:00:00 +0000\n"
        "From: Ada <ada@example.test>\n"
        "To: User <user@example.test>\n"
        "Subject: Review today\n\n"
        "Please review this today."
    )

    email = load_eml_email(path)

    assert email.source == EmailSource.FILE
    assert email.provider_message_id == "<real-1@example.test>"
    assert email.sender.email == "ada@example.test"
    assert email.recipients[0].email == "user@example.test"
    assert email.body_raw.strip() == "Please review this today."


def test_load_eml_email_falls_back_to_html_body(tmp_path: Path) -> None:
    path = tmp_path / "message.eml"
    path.write_text(
        "Message-ID: <real-html@example.test>\n"
        "From: ada@example.test\n"
        "To: user@example.test\n"
        "Subject: HTML only\n"
        "MIME-Version: 1.0\n"
        'Content-Type: multipart/alternative; boundary="boundary"\n\n'
        "--boundary\n"
        "Content-Type: text/html; charset=utf-8\n\n"
        "<html><body><p>Please review this today.</p></body></html>\n"
        "--boundary--\n"
    )

    email = load_eml_email(path)

    assert "Please review this today" in email.body_raw


def test_load_eml_email_skips_empty_plain_part_for_html_body(tmp_path: Path) -> None:
    path = tmp_path / "message.eml"
    path.write_text(
        "Message-ID: <real-empty-plain@example.test>\n"
        "From: ada@example.test\n"
        "To: user@example.test\n"
        "Subject: HTML fallback\n"
        "MIME-Version: 1.0\n"
        'Content-Type: multipart/alternative; boundary="boundary"\n\n'
        "--boundary\n"
        "Content-Type: text/plain; charset=utf-8\n\n"
        "\n"
        "--boundary\n"
        "Content-Type: text/html; charset=utf-8\n\n"
        "<html><body><p>Please pay this bill.</p></body></html>\n"
        "--boundary--\n"
    )

    email = load_eml_email(path)

    assert "Please pay this bill" in email.body_raw


def test_import_eml_emails_limits_and_skips_duplicates(tmp_path: Path) -> None:
    session_factory = make_session_factory(build_settings(tmp_path))
    Base.metadata.create_all(session_factory.kw["bind"])
    path = tmp_path / "message.eml"
    path.write_text(
        "Message-ID: <real-1@example.test>\n"
        "From: ada@example.test\n"
        "To: user@example.test\n"
        "Subject: Review\n\n"
        "Body"
    )

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        first_import = import_eml_emails([path], repository)
        second_import = import_eml_emails([path], repository)

    assert len(first_import) == 1
    assert second_import == []

    with pytest.raises(ValueError, match="limited"):
        with session_factory.begin() as session:
            import_eml_emails([path, path], SqlAlchemyRepository(session), limit=1)
