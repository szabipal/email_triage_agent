from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from email_agent.domain import (
    CalendarEventProposal,
    Email,
    EmailAnalysisSignals,
    EmailSource,
)
from email_agent.ingestion.local import load_rfc822_email
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository

READONLY_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
MODIFY_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

CATEGORY_LABELS: dict[str, tuple[str, str]] = {
    "automated invoice notification": ("AI/Billing", "#fad165"),
    "billing_payment_issue": ("AI/Billing", "#fad165"),
    "job_alert": ("AI/Jobs", "#16a765"),
    "job_recommendation": ("AI/Jobs", "#16a765"),
    "meeting": ("AI/Meeting", "#4986e7"),
    "newsletter": ("AI/Newsletter", "#b6cff5"),
    "promotional_marketing": ("AI/Promotion", "#f2f2f2"),
    "promotional_travel_offer": ("AI/Promotion", "#f2f2f2"),
    "security_alert": ("AI/Security", "#fb4c2f"),
    "work": ("AI/Work", "#4986e7"),
}

LABEL_COLORS: dict[str, dict[str, str]] = {
    "AI/Action Required": {"textColor": "#ffffff", "backgroundColor": "#fb4c2f"},
    "AI/Billing": {"textColor": "#000000", "backgroundColor": "#fad165"},
    "AI/Calendar": {"textColor": "#ffffff", "backgroundColor": "#4986e7"},
    "AI/Jobs": {"textColor": "#ffffff", "backgroundColor": "#16a765"},
    "AI/Meeting": {"textColor": "#ffffff", "backgroundColor": "#4986e7"},
    "AI/Newsletter": {"textColor": "#000000", "backgroundColor": "#b6cff5"},
    "AI/Promotion": {"textColor": "#000000", "backgroundColor": "#f2f2f2"},
    "AI/Security": {"textColor": "#ffffff", "backgroundColor": "#fb4c2f"},
    "AI/Work": {"textColor": "#ffffff", "backgroundColor": "#4986e7"},
}


@dataclass(frozen=True)
class GmailLabelAssignment:
    gmail_message_id: str
    label_names: list[str]


class GmailSyncError(RuntimeError):
    pass


def import_gmail_unread(
    repository: SqlAlchemyRepository,
    *,
    credentials_path: Path,
    token_path: Path,
    query: str = "label:UNREAD",
    limit: int = 10,
    write_enabled: bool = False,
) -> list[Email]:
    service = _gmail_service(
        credentials_path,
        token_path,
        scopes=MODIFY_SCOPES if write_enabled else READONLY_SCOPES,
    )
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


def gmail_label_names(
    signals: EmailAnalysisSignals,
    calendar_proposals: list[CalendarEventProposal],
) -> list[str]:
    labels = [CATEGORY_LABELS.get(signals.category, ("AI/Other", "#cccccc"))[0]]
    if signals.action_required:
        labels.append("AI/Action Required")
    if calendar_proposals:
        labels.append("AI/Calendar")
    return list(dict.fromkeys(labels))


def apply_gmail_labels(
    assignments: list[GmailLabelAssignment],
    *,
    credentials_path: Path,
    token_path: Path,
) -> int:
    if not assignments:
        return 0

    service = _gmail_service(credentials_path, token_path, scopes=MODIFY_SCOPES)
    label_ids = _ensure_labels(service, sorted(_all_label_names(assignments)))
    labeled = 0
    for assignment in assignments:
        ids = [label_ids[name] for name in assignment.label_names if name in label_ids]
        if not ids:
            continue
        service.users().messages().modify(
            userId="me",
            id=assignment.gmail_message_id,
            body={"addLabelIds": ids},
        ).execute()
        labeled += 1
    return labeled


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


def _all_label_names(assignments: list[GmailLabelAssignment]) -> set[str]:
    return {label for assignment in assignments for label in assignment.label_names}


def _ensure_labels(service, label_names: list[str]) -> dict[str, str]:
    existing = {
        label["name"]: label["id"]
        for label in service.users()
        .labels()
        .list(userId="me")
        .execute()
        .get("labels", [])
    }
    for name in label_names:
        if name in existing:
            continue
        label = (
            service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                    "color": LABEL_COLORS.get(
                        name,
                        {"textColor": "#000000", "backgroundColor": "#cccccc"},
                    ),
                },
            )
            .execute()
        )
        existing[name] = label["id"]
    return existing


def _gmail_service(credentials_path: Path, token_path: Path, *, scopes: list[str]):
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
        credentials = Credentials.from_authorized_user_file(str(token_path), scopes)
        if not credentials.has_scopes(scopes):
            credentials = None

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                scopes,
            )
            credentials = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json())

    return build("gmail", "v1", credentials=credentials)
