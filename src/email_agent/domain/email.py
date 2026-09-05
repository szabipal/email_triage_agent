from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EmailSource(StrEnum):
    FIXTURE = "fixture"
    FILE = "file"
    CONTROLLED_API = "controlled_api"
    GMAIL = "gmail"


class ProcessedEmailStatus(StrEnum):
    PROCESSED = "processed"
    FAILED = "failed"


class LowValueType(StrEnum):
    SPAM_LIKE = "spam-like"
    NEWSLETTER = "newsletter"
    AUTOMATED_NOTIFICATION = "automated_notification"
    OTHER_LOW_VALUE = "other_low_value"


class RetrievalMethod(StrEnum):
    RAG = "rag"
    THREAD = "thread"


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


class ProcessedEmail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    normalized_subject: str
    normalized_body: str
    processed_at: datetime
    status: ProcessedEmailStatus

    body_without_quotes: str | None = None
    signature_removed: bool | None = None
    detected_language: str | None = None
    language_confidence: float | None = Field(default=None, ge=0, le=1)
    locale_hint: str | None = None
    processing_errors: list[str] = Field(default_factory=list)


class RetrievedContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    source_email_ids: list[str] = Field(min_length=1)
    query_email_id: str = Field(min_length=1)
    retrieval_method: RetrievalMethod
    summary: str
    relevance_score: float

    snippet_text: str | None = None
    rank: int | None = Field(default=None, ge=1)
    embedding_model: str | None = None
    retrieval_query: str | None = None
    skip_reason: str | None = None

    @model_validator(mode="after")
    def validate_current_email_excluded(self) -> RetrievedContext:
        if self.query_email_id in self.source_email_ids:
            raise ValueError("source_email_ids must exclude query_email_id")

        return self


class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    owner: str | None = None
    due_at: datetime | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_excerpt: str | None = None


class DeadlineCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    due_at: datetime | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_excerpt: str | None = None
    uncertainty: str | None = None


class MeetingCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    attendees: list[EmailIdentity] = Field(default_factory=list)
    location: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_excerpt: str | None = None
    uncertainty: str | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> MeetingCandidate:
        if (
            self.start_at is not None
            and self.end_at is not None
            and self.end_at < self.start_at
        ):
            raise ValueError("end_at must be after start_at")

        return self


class EmailAnalysisSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    processed_email_id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    category: str = Field(min_length=1)
    action_required: bool
    low_value_type: LowValueType | None
    confidence: float = Field(ge=0, le=1)

    action_items: list[ActionItem] = Field(default_factory=list)
    deadlines: list[DeadlineCandidate] = Field(default_factory=list)
    meeting_details: list[MeetingCandidate] = Field(default_factory=list)
    semantic_flags: list[str] = Field(default_factory=list)
    source_language: str | None = None
    output_language: str | None = None
    translation_notes: str | None = None
    model_name: str | None = None
    prompt_version: str | None = None
    schema_version: str | None = None


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
