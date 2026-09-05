from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EmailRecord(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    provider_message_id: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    sender: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    recipients: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    body_raw: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class EmailThreadRecord(Base):
    __tablename__ = "email_threads"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    subject_key: Mapped[str] = mapped_column(String, nullable=False)
    email_ids: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class ProcessedEmailRecord(Base):
    __tablename__ = "processed_emails"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email_id: Mapped[str] = mapped_column(ForeignKey("emails.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    normalized_subject: Mapped[str] = mapped_column(String, nullable=False)
    normalized_body: Mapped[str] = mapped_column(Text, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class RetrievedContextRecord(Base):
    __tablename__ = "retrieved_contexts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    query_email_id: Mapped[str] = mapped_column(ForeignKey("emails.id"), nullable=False)
    source_email_ids: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    retrieval_method: Mapped[str] = mapped_column(String, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class AnalysisSignalsRecord(Base):
    __tablename__ = "analysis_signals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    processed_email_id: Mapped[str] = mapped_column(
        ForeignKey("processed_emails.id"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String, nullable=False)
    action_required: Mapped[bool] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class PriorityResultRecord(Base):
    __tablename__ = "priority_results"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email_id: Mapped[str] = mapped_column(ForeignKey("emails.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    band: Mapped[str] = mapped_column(String, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ruleset_version: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class UserPreferenceRecord(Base):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    preference_type: Mapped[str] = mapped_column(String, nullable=False)
    effect: Mapped[str] = mapped_column(String, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class ProposedActionRecord(Base):
    __tablename__ = "proposed_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email_id: Mapped[str] = mapped_column(ForeignKey("emails.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class CalendarEventProposalRecord(Base):
    __tablename__ = "calendar_event_proposals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email_id: Mapped[str] = mapped_column(ForeignKey("emails.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    provider_event_id: Mapped[str | None] = mapped_column(String)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class ToolApprovalRecord(Base):
    __tablename__ = "tool_approvals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    proposal_id: Mapped[str] = mapped_column(
        ForeignKey("calendar_event_proposals.id"),
        nullable=False,
    )
    tool_name: Mapped[str] = mapped_column(String, nullable=False)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    execution_status: Mapped[str | None] = mapped_column(String)
    external_result_id: Mapped[str | None] = mapped_column(String)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
