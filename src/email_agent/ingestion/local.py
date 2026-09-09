from __future__ import annotations

from datetime import UTC, datetime
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from hashlib import sha256
from pathlib import Path

from email_agent.domain import Email, EmailIdentity, EmailSource
from email_agent.evaluation import validate_fixture_file
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository


def load_fixture_emails(path: Path) -> list[Email]:
    return [record.email for record in validate_fixture_file(path)]


def import_fixture_emails(
    path: Path,
    repository: SqlAlchemyRepository,
) -> list[Email]:
    imported: list[Email] = []
    seen_provider_ids = _existing_provider_message_ids(repository)

    for email in load_fixture_emails(path):
        if email.provider_message_id in seen_provider_ids:
            continue

        repository.save_email(email)
        imported.append(email)
        seen_provider_ids.add(email.provider_message_id)

    return imported


def load_eml_email(path: Path) -> Email:
    return load_rfc822_email(
        path.read_bytes(),
        fallback_provider_message_id=str(path.resolve()),
    )


def load_rfc822_email(
    data: bytes,
    *,
    fallback_provider_message_id: str,
    source: EmailSource = EmailSource.FILE,
) -> Email:
    message = BytesParser(policy=policy.default).parsebytes(data)
    message_id = str(message.get("Message-ID") or fallback_provider_message_id)
    received_at = _parsed_date(str(message.get("Date") or ""))
    body = _plain_body(message)
    sender = _identities(str(message.get("From") or "")) or [
        EmailIdentity(email="unknown@example.invalid")
    ]
    recipients = _identities(str(message.get("To") or "")) or [
        EmailIdentity(email="user@example.invalid")
    ]

    return Email(
        id=f"eml-{sha256(message_id.encode()).hexdigest()[:16]}",
        provider_message_id=message_id,
        subject=str(message.get("Subject") or ""),
        sender=sender[0],
        recipients=recipients,
        received_at=received_at,
        body_raw=body,
        source=source,
        cc=_identities(str(message.get("Cc") or "")),
        reply_to=(_identities(str(message.get("Reply-To") or "")) or [None])[0],
        headers={key: str(value) for key, value in message.items()},
    )


def import_eml_emails(
    paths: list[Path],
    repository: SqlAlchemyRepository,
    *,
    limit: int = 5,
) -> list[Email]:
    if len(paths) > limit:
        raise ValueError(f"import is limited to {limit} .eml files")

    imported: list[Email] = []
    seen_provider_ids = _existing_provider_message_ids(repository)
    for path in paths:
        if path.suffix.lower() != ".eml" or not path.is_file():
            raise ValueError(f"{path} is not an .eml file")
        email = load_eml_email(path)
        if email.provider_message_id in seen_provider_ids:
            continue
        repository.save_email(email)
        imported.append(email)
        seen_provider_ids.add(email.provider_message_id)
    return imported


def _existing_provider_message_ids(repository: SqlAlchemyRepository) -> set[str]:
    return {email.provider_message_id for email in repository.list_emails()}


def _parsed_date(value: str) -> datetime:
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return datetime.now(UTC)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _identities(value: str) -> list[EmailIdentity]:
    return [
        EmailIdentity(email=address, display_name=name or None)
        for name, address in getaddresses([value])
        if address
    ]


def _plain_body(message) -> str:
    if message.is_multipart():
        html_body = ""
        for part in message.walk():
            content_type = part.get_content_type()
            content = str(part.get_content()) if not part.is_multipart() else ""
            if content_type == "text/plain" and content.strip():
                return content
            if not html_body and content_type == "text/html" and content.strip():
                html_body = content
        return html_body
    return str(message.get_content())
