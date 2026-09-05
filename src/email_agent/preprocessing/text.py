from __future__ import annotations

from datetime import UTC, datetime
from html.parser import HTMLParser

from email_agent.domain import Email, ProcessedEmail, ProcessedEmailStatus


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def normalize_email(email: Email) -> ProcessedEmail:
    body = (
        html_to_text(email.body_raw)
        if _looks_like_html(email.body_raw)
        else email.body_raw
    )
    return ProcessedEmail(
        id=f"processed-{email.id}",
        email_id=email.id,
        normalized_subject=email.subject.strip(),
        normalized_body=collapse_whitespace(body),
        processed_at=datetime.now(UTC),
        status=ProcessedEmailStatus.PROCESSED,
    )


def html_to_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value)
    return " ".join(parser.parts)


def collapse_whitespace(value: str) -> str:
    return " ".join(value.split())


def _looks_like_html(value: str) -> bool:
    return "<" in value and ">" in value
