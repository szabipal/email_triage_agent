from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from email_agent.config import Settings

DEFAULT_PRIORITY_WEIGHTS = {
    "action_required": 35.0,
    "deadline": 30.0,
    "meeting": 25.0,
    "context": 10.0,
    "preference": 10.0,
    "low_value": -50.0,
}
DEFAULT_PRIORITY_THRESHOLDS = {"high": 70.0, "normal": 30.0}


class PriorityScoringConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weights: dict[str, float] = Field(default_factory=lambda: DEFAULT_PRIORITY_WEIGHTS.copy())
    thresholds: dict[str, float] = Field(default_factory=lambda: DEFAULT_PRIORITY_THRESHOLDS.copy())

    @model_validator(mode="after")
    def validate_config(self) -> "PriorityScoringConfig":
        unknown = set(self.weights) - set(DEFAULT_PRIORITY_WEIGHTS)
        if unknown:
            raise ValueError(f"unknown priority weights: {sorted(unknown)}")
        if self.thresholds["high"] <= self.thresholds["normal"]:
            raise ValueError("high threshold must exceed normal threshold")
        return self


def load_priority_config(settings: Settings) -> PriorityScoringConfig:
    return PriorityScoringConfig(
        weights=DEFAULT_PRIORITY_WEIGHTS | settings.priority_weights,
        thresholds=DEFAULT_PRIORITY_THRESHOLDS,
    )
