from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

JsonValue = str | int | float | bool | None | list[object] | dict[str, object]


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


class PreferenceEffect(StrEnum):
    BOOST = "boost"
    PENALIZE = "penalize"
    DISPLAY = "display"


class PreferenceType(StrEnum):
    SENDER = "sender"
    CATEGORY = "category"
    KEYWORD = "keyword"
    OUTPUT_LANGUAGE = "output_language"
    LOCALE = "locale"
    TIMEZONE = "timezone"


class PriorityBand(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class PriorityFactorDirection(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ProposedActionType(StrEnum):
    TASK = "task"
    FOLLOW_UP = "follow_up"
    DECISION = "decision"
    OTHER = "other"


class ProposedActionSource(StrEnum):
    ANALYSIS = "analysis"
    USER = "user"


class ProposedActionStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"


class CalendarProposalStatus(StrEnum):
    PENDING = "pending"
    INCOMPLETE = "incomplete"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"


class CalendarProposalSource(StrEnum):
    DEADLINE = "deadline"
    MEETING = "meeting"


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ExecutionStatus(StrEnum):
    NOT_STARTED = "not_started"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"


class EmailAnalysisStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


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


class UserPreference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    preference_type: PreferenceType
    value: JsonValue
    effect: PreferenceEffect
    weight: float
    enabled: bool

    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> UserPreference:
        if (
            self.created_at is not None
            and self.expires_at is not None
            and self.expires_at < self.created_at
        ):
            raise ValueError("expires_at must be after created_at")

        return self


class PriorityFactor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    direction: PriorityFactorDirection
    weight: float
    source_ids: list[str] = Field(default_factory=list)
    details: JsonValue = None


class PriorityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    score: float
    band: PriorityBand
    factors: list[PriorityFactor] = Field(min_length=1)
    calculated_at: datetime
    ruleset_version: str = Field(min_length=1)

    preference_matches: list[str] = Field(default_factory=list)
    context_influence: str | None = None
    deadline_urgency: str | None = None
    low_value_penalty: str | None = None
    recalculated_from_id: str | None = None


class EmailAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    processed_email_id: str = Field(min_length=1)
    signals_id: str = Field(min_length=1)
    priority_result_id: str = Field(min_length=1)
    status: EmailAnalysisStatus

    retrieved_context_ids: list[str] = Field(default_factory=list)
    calendar_proposal_ids: list[str] = Field(default_factory=list)
    explanation: str | None = None
    errors: list[str] = Field(default_factory=list)
    completed_at: datetime | None = None


class ProposedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    action_type: ProposedActionType
    source: ProposedActionSource

    owner: str | None = None
    due_at: datetime | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_excerpt: str | None = None
    status: ProposedActionStatus | None = None


class CalendarEventProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    start_at: datetime | None
    status: CalendarProposalStatus
    source: CalendarProposalSource

    end_at: datetime | None = None
    timezone: str | None = None
    location: str | None = None
    attendees: list[EmailIdentity] = Field(default_factory=list)
    description: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)
    locale_assumption: str | None = None
    time_ambiguity: str | None = None
    provider_event_id: str | None = None

    @property
    def can_execute(self) -> bool:
        return self.status == CalendarProposalStatus.APPROVED

    @model_validator(mode="after")
    def validate_event_state(self) -> CalendarEventProposal:
        if self.status != CalendarProposalStatus.INCOMPLETE and self.start_at is None:
            raise ValueError("start_at is required unless status is incomplete")

        if (
            self.start_at is not None
            and self.end_at is not None
            and self.end_at < self.start_at
        ):
            raise ValueError("end_at must be after start_at")

        return self


class ToolApproval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    proposal_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    decision: ApprovalDecision
    decided_at: datetime
    decided_by: str = Field(min_length=1)

    approval_notes: str | None = None
    execution_status: ExecutionStatus | None = None
    execution_error: str | None = None
    external_result_id: str | None = None


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
