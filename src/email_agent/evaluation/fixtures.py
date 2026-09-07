from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from email_agent.domain import (
    ActionItem,
    DeadlineCandidate,
    Email,
    LowValueType,
    MeetingCandidate,
    PriorityBand,
)


class DatasetSplit(StrEnum):
    DEV = "dev"
    TEST = "test"


class EvaluationLabels(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str | None = None
    category: str = Field(min_length=1)
    action_required: bool
    low_value_type: LowValueType | None = None
    priority_band: PriorityBand

    action_items: list[ActionItem] = Field(default_factory=list)
    deadlines: list[DeadlineCandidate] = Field(default_factory=list)
    meeting_details: list[MeetingCandidate] = Field(default_factory=list)
    expected_related_source_email_ids: list[str] = Field(default_factory=list)
    retrieval_should_run: bool = False
    supported_language: bool = True
    malformed_expected: bool = False

    @model_validator(mode="after")
    def validate_retrieval_labels(self) -> EvaluationLabels:
        if self.expected_related_source_email_ids and not self.retrieval_should_run:
            raise ValueError(
                "retrieval_should_run must be true when related sources are labelled"
            )

        return self


class FixtureRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    split: DatasetSplit
    scenario_ids: list[str] = Field(min_length=1)
    email: Email
    labels: EvaluationLabels
    notes: str | None = None

    @model_validator(mode="after")
    def validate_no_current_email_leakage(self) -> FixtureRecord:
        if self.email.id in self.labels.expected_related_source_email_ids:
            raise ValueError("expected related sources must exclude current email")

        return self
