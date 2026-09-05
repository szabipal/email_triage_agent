from datetime import UTC, datetime

from email_agent.domain import Email, EmailIdentity, EmailSource, ProcessedEmailStatus
from email_agent.persistence import make_session_factory
from email_agent.persistence.models import Base
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository
from email_agent.preprocessing import normalize_email, preprocess_batch


def make_email(body_raw: str, subject: str = " Hello ") -> Email:
    return Email(
        id="email-1",
        provider_message_id="provider-1",
        subject=subject,
        sender=EmailIdentity(email="ada@example.com"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 2, tzinfo=UTC),
        body_raw=body_raw,
        source=EmailSource.FIXTURE,
    )


def test_normalize_email_converts_html_body_to_text() -> None:
    processed = normalize_email(make_email("<p>Hello <strong>there</strong>.</p>"))

    assert processed.status == ProcessedEmailStatus.PROCESSED
    assert processed.normalized_subject == "Hello"
    assert processed.normalized_body == "Hello there ."
    assert processed.email_id == "email-1"


def test_normalize_email_removes_quoted_reply_and_signature() -> None:
    processed = normalize_email(
        make_email(
            "Please review this.\n\n--\nAda\n\nOn Mon, Bob wrote:\n> old message"
        )
    )

    assert processed.normalized_body == "Please review this."
    assert processed.body_without_quotes == "Please review this. -- Ada"
    assert processed.signature_removed is True


def test_normalize_email_detects_fixture_languages() -> None:
    hungarian = normalize_email(
        make_email("Szia, kérlek nézd át a szerződést péntekig."),
        locale_hint="hu_HU",
    )
    spanish = normalize_email(
        make_email("¿Puedes unirte a la reunión el jueves?"),
        locale_hint="es_ES",
    )

    assert hungarian.detected_language == "hu"
    assert hungarian.locale_hint == "hu_HU"
    assert spanish.detected_language == "es"
    assert spanish.locale_hint == "es_ES"


def test_preprocess_batch_isolates_empty_body_failure(tmp_path) -> None:
    from email_agent.config import Settings

    settings = Settings(
        **{
            "_env_file": None,
            "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}",
        }
    )
    session_factory = make_session_factory(settings)
    Base.metadata.create_all(session_factory.kw["bind"])
    valid = make_email("Please review.", subject="Valid")
    invalid = make_email("", subject="Invalid")
    invalid.id = "email-2"
    invalid.provider_message_id = "provider-2"

    with session_factory.begin() as session:
        repository = SqlAlchemyRepository(session)
        repository.save_email(valid)
        repository.save_email(invalid)

        processed = preprocess_batch([valid, invalid], repository)

    assert [item.status for item in processed] == [
        ProcessedEmailStatus.PROCESSED,
        ProcessedEmailStatus.FAILED,
    ]
    assert processed[1].processing_errors == ["email body is empty"]
