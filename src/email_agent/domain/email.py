from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EmailSource(StrEnum):
    FIXTURE = "fixture"
    FILE = "file"
    CONTROLLED_API = "controlled_api"
    GMAIL = "gmail"


class EmailIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1)
    display_name: str | None = None


class EmailAttachmentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str | None = None
    content_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)


class Email(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    provider_message_id: str = Field(min_length=1)
    subject: str
    sender: EmailIdentity
    recipients: list[EmailIdentity] = Field(min_length=1)
    received_at: datetime
    body_raw: str
    source: EmailSource

    cc: list[EmailIdentity] = Field(default_factory=list)
    bcc: list[EmailIdentity] = Field(default_factory=list)
    reply_to: EmailIdentity | None = None
    thread_id: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    attachments_metadata: list[EmailAttachmentMetadata] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)


class EmailThread(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    subject_key: str = Field(min_length=1)
    email_ids: list[str] = Field(min_length=1)

    provider_thread_id: str | None = None
    participants: list[EmailIdentity] = Field(default_factory=list)
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    summary: str | None = None

    @model_validator(mode="after")
    def validate_seen_range(self) -> EmailThread:
        if (
            self.first_seen_at is not None
            and self.last_seen_at is not None
            and self.last_seen_at < self.first_seen_at
        ):
            raise ValueError("last_seen_at must be after first_seen_at")

        return self
