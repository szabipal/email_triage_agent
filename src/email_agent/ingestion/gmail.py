from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from email_agent.domain import Email, EmailSource
from email_agent.ingestion.local import load_rfc822_email
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailSyncError(RuntimeError):
    pass


def import_gmail_unread(
    repository: SqlAlchemyRepository,
    *,
    credentials_path: Path,
    token_path: Path,
    query: str = "label:UNREAD",
    limit: int = 10,
) -> list[Email]:
    service = _gmail_service(credentials_path, token_path)
    response = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=limit)
        .execute()
    )
    messages = response.get("messages", [])
    seen_provider_ids = {
        email.provider_message_id for email in repository.list_emails()
    }
    imported: list[Email] = []

    for message in messages:
        gmail_id = str(message["id"])
        provider_message_id = f"gmail:{gmail_id}"
        if provider_message_id in seen_provider_ids:
            continue

        raw_message = (
            service.users()
            .messages()
            .get(userId="me", id=gmail_id, format="raw")
            .execute()
        )
        email = _email_from_raw_message(raw_message, provider_message_id)
        repository.save_email(email)
        imported.append(email)
        seen_provider_ids.add(provider_message_id)

    return imported


def _email_from_raw_message(
    raw_message: dict[str, Any],
    provider_message_id: str,
) -> Email:
    raw = raw_message.get("raw")
    if not isinstance(raw, str) or not raw:
        raise GmailSyncError("Gmail message did not include raw RFC822 content")

    data = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    email = load_rfc822_email(
        data,
        fallback_provider_message_id=provider_message_id,
        source=EmailSource.GMAIL,
    )
    return email.model_copy(update={"provider_message_id": provider_message_id})


def _gmail_service(credentials_path: Path, token_path: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as error:
        raise GmailSyncError(
            "Gmail sync dependencies are not installed. Run `uv sync --locked`."
        ) from error

    if not credentials_path.is_file():
        raise GmailSyncError(f"Gmail credentials file not found: {credentials_path}")

    credentials = None
    if token_path.is_file():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json())

    return build("gmail", "v1", credentials=credentials)
