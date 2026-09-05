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


def normalize_email(email: Email, *, locale_hint: str = "en_US") -> ProcessedEmail:
    body = (
        html_to_text(email.body_raw)
        if _looks_like_html(email.body_raw)
        else email.body_raw
    )
    body_without_quotes = strip_quoted_reply(body)
    cleaned_body, signature_removed = strip_signature(body_without_quotes)
    language, confidence = detect_language(cleaned_body)
    return ProcessedEmail(
        id=f"processed-{email.id}",
        email_id=email.id,
        normalized_subject=email.subject.strip(),
        normalized_body=collapse_whitespace(cleaned_body),
        processed_at=datetime.now(UTC),
        status=ProcessedEmailStatus.PROCESSED,
        body_without_quotes=collapse_whitespace(body_without_quotes),
        signature_removed=signature_removed,
        detected_language=language,
        language_confidence=confidence,
        locale_hint=locale_hint,
    )


def html_to_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value)
    return " ".join(parser.parts)


def collapse_whitespace(value: str) -> str:
    return " ".join(value.split())


def strip_quoted_reply(value: str) -> str:
    lines = []
    for line in value.splitlines():
        stripped = line.strip()
        if (
            stripped.startswith(">")
            or stripped.lower().startswith("on ")
            and "wrote:" in stripped.lower()
        ):
            break
        lines.append(line)
    return "\n".join(lines)


def strip_signature(value: str) -> tuple[str, bool]:
    lines = value.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "--":
            return "\n".join(lines[:index]), True
    return value, False


def detect_language(value: str) -> tuple[str | None, float | None]:
    lowered = value.lower()
    if any(token in lowered for token in (" kérlek ", " szerződés", " szia")):
        return "hu", 0.8
    if any(token in lowered for token in ("¿", " reunión", " puedes ")):
        return "es", 0.8
    if value.strip():
        return "en", 0.6
    return None, None


def _looks_like_html(value: str) -> bool:
    return "<" in value and ">" in value
