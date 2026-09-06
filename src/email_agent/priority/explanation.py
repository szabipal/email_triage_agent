from __future__ import annotations

from email_agent.domain import PriorityFactorDirection, PriorityResult


def build_priority_explanation(result: PriorityResult) -> str:
    positives = [
        factor.name.replace("_", " ")
        for factor in result.factors
        if factor.direction == PriorityFactorDirection.POSITIVE
    ]
    negatives = [
        factor.name.replace("_", " ")
        for factor in result.factors
        if factor.direction == PriorityFactorDirection.NEGATIVE
    ]
    parts = [f"Priority is {result.band.value} with score {result.score:.0f}."]
    if positives:
        parts.append(f"Raised by {', '.join(positives)}.")
    if negatives:
        parts.append(f"Lowered by {', '.join(negatives)}.")
    return " ".join(parts)
