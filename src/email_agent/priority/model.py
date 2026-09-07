from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from email_agent.domain import EmailAnalysisSignals, RetrievedContext, UserPreference


class PriorityScoringInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email_id: str
    signals: EmailAnalysisSignals
    retrieved_context: list[RetrievedContext] = []
    preferences: list[UserPreference] = []
