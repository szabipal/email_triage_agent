from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from email_agent.domain import (
    CalendarEventProposal,
    Email,
    EmailAnalysis,
    PriorityBand,
    PriorityFactor,
    RetrievedContext,
)


class ApiError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str


class Page(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    items: list[object]


class InboxItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email_id: str
    subject: str
    sender: str
    received_at: datetime
    summary: str
    category: str
    action_required: bool
    priority_band: PriorityBand
    priority_score: float


class EmailDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Email
    analysis: EmailAnalysis
    factors: list[PriorityFactor]
    retrieved_context: list[RetrievedContext] = []
    proposals: list[CalendarEventProposal] = []
