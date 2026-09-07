from datetime import UTC, datetime

from email_agent.domain import (
    PriorityBand,
    PriorityFactor,
    PriorityFactorDirection,
    PriorityResult,
)
from email_agent.priority import build_priority_explanation


def test_priority_explanation_uses_stored_factors() -> None:
    explanation = build_priority_explanation(
        PriorityResult(
            id="priority-1",
            email_id="email-1",
            score=85,
            band=PriorityBand.HIGH,
            factors=[
                PriorityFactor(
                    name="action_required",
                    direction=PriorityFactorDirection.POSITIVE,
                    weight=35,
                    source_ids=["signals-1"],
                ),
                PriorityFactor(
                    name="deadline",
                    direction=PriorityFactorDirection.POSITIVE,
                    weight=30,
                    source_ids=["signals-1"],
                ),
            ],
            calculated_at=datetime(2026, 1, 1, tzinfo=UTC),
            ruleset_version="priority-v1",
        )
    )

    assert explanation == (
        "Priority is high with score 85. Raised by action required, deadline."
    )
