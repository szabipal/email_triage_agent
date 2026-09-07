from __future__ import annotations

from pathlib import Path

from email_agent.domain import Email, EmailSource
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


def _existing_provider_message_ids(repository: SqlAlchemyRepository) -> set[str]:
    return {
        email.provider_message_id
        for email in repository.list_emails()
        if email.source == EmailSource.FIXTURE
    }
