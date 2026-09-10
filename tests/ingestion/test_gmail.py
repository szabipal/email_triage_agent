import base64
from datetime import UTC, datetime
from pathlib import Path

from email_agent.domain import (
    CalendarEventProposal,
    CalendarProposalSource,
    CalendarProposalStatus,
    EmailAnalysisSignals,
    EmailSource,
)
from email_agent.ingestion.gmail import (
    GmailLabelAssignment,
    _email_from_raw_message,
    apply_gmail_labels,
    gmail_label_names,
)


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


def test_apply_gmail_labels_creates_missing_labels_and_modifies_messages(
    monkeypatch,
) -> None:
    service = FakeGmailService(
        existing_labels=[{"id": "label-newsletter", "name": "AI/Newsletter"}]
    )
    monkeypatch.setattr(
        "email_agent.ingestion.gmail._gmail_service",
        lambda *args, **kwargs: service,
    )

    labeled = apply_gmail_labels(
        [
            GmailLabelAssignment(
                gmail_message_id="gmail-1",
                label_names=["AI/Newsletter", "AI/Action Required"],
            )
        ],
        credentials_path=Path("credentials.json"),
        token_path=Path("token.json"),
    )

    assert labeled == 1
    assert service.created_labels[0]["name"] == "AI/Action Required"
    assert service.modified_messages == [
        {
            "id": "gmail-1",
            "body": {"addLabelIds": ["label-newsletter", "created-1"]},
        }
    ]


def test_gmail_label_names_include_category_action_and_calendar() -> None:
    signals = EmailAnalysisSignals(
        id="signals-1",
        processed_email_id="processed-1",
        summary="Billing asks for payment.",
        category="billing_payment_issue",
        action_required=True,
        low_value_type=None,
        confidence=0.9,
    )
    proposal = CalendarEventProposal(
        id="proposal-1",
        email_id="email-1",
        title="Pay bill",
        start_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=CalendarProposalStatus.PENDING,
        source=CalendarProposalSource.DEADLINE,
    )

    labels = gmail_label_names(signals, calendar_proposals=[proposal])

    assert labels == ["AI/Billing", "AI/Action Required", "AI/Calendar"]


class FakeGmailService:
    def __init__(self, *, existing_labels):
        self.existing_labels = existing_labels
        self.created_labels = []
        self.modified_messages = []

    def users(self):
        return self

    def labels(self):
        return self

    def messages(self):
        return self

    def list(self, **kwargs):
        self._response = {"labels": self.existing_labels}
        return self

    def create(self, **kwargs):
        label = kwargs["body"] | {"id": f"created-{len(self.created_labels) + 1}"}
        self.created_labels.append(label)
        self._response = label
        return self

    def modify(self, **kwargs):
        self.modified_messages.append({"id": kwargs["id"], "body": kwargs["body"]})
        self._response = {}
        return self

    def execute(self):
        return self._response
