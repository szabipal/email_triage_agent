from datetime import UTC, datetime

from email_agent.domain import Email, EmailIdentity, EmailSource
from email_agent.persistence import EmailRepository


class InMemoryEmailRepository:
    def __init__(self) -> None:
        self.emails: dict[str, Email] = {}

    def save_email(self, email: Email) -> None:
        self.emails[email.id] = email

    def get_email(self, email_id: str) -> Email | None:
        return self.emails.get(email_id)

    def list_emails(self) -> list[Email]:
        return list(self.emails.values())


def test_service_can_depend_on_email_repository_protocol() -> None:
    repository: EmailRepository = InMemoryEmailRepository()
    email = Email(
        id="email-1",
        provider_message_id="provider-1",
        subject="Hello",
        sender=EmailIdentity(email="ada@example.com"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 2, tzinfo=UTC),
        body_raw="Hello",
        source=EmailSource.FIXTURE,
    )

    repository.save_email(email)

    assert repository.get_email("email-1") == email
