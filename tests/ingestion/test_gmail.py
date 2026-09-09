import base64

from email_agent.domain import EmailSource
from email_agent.ingestion.gmail import _email_from_raw_message


def test_email_from_raw_message_decodes_rfc822_content() -> None:
    raw = (
        b"Message-ID: <gmail-1@example.test>\n"
        b"From: ada@example.test\n"
        b"To: user@example.test\n"
        b"Subject: Pay bill\n\n"
        b"Please pay this bill today."
    )
    raw_message = {
        "raw": base64.urlsafe_b64encode(raw).decode().rstrip("="),
    }

    email = _email_from_raw_message(raw_message, "gmail:gmail-1")

    assert email.source == EmailSource.GMAIL
    assert email.provider_message_id == "gmail:gmail-1"
    assert email.subject == "Pay bill"
    assert email.body_raw.strip() == "Please pay this bill today."
