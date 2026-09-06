from __future__ import annotations

from datetime import UTC, datetime

from email_agent.domain import (
    PreferenceEffect,
    PreferenceType,
    PriorityBand,
    PriorityFactor,
    PriorityFactorDirection,
    PriorityResult,
)
from email_agent.priority.config import PriorityScoringConfig
from email_agent.priority.model import PriorityScoringInput


def score_priority(
    input_: PriorityScoringInput,
    config: PriorityScoringConfig | None = None,
    *,
    calculated_at: datetime | None = None,
) -> PriorityResult:
    config = config or PriorityScoringConfig()
    factors = _factors(input_, config)
    score = max(0.0, min(100.0, 40.0 + sum(factor.weight for factor in factors)))
    return PriorityResult(
        id=f"priority-{input_.email_id}",
        email_id=input_.email_id,
        score=score,
        band=_band(score, config),
        factors=factors,
        calculated_at=calculated_at or datetime.now(UTC),
        ruleset_version="priority-v1",
        preference_matches=[
            source_id
            for factor in factors
            if factor.name.startswith("preference")
            for source_id in factor.source_ids
        ],
        context_influence="context used" if input_.retrieved_context else None,
        deadline_urgency="deadline present" if input_.signals.deadlines else None,
        low_value_penalty="low-value message" if input_.signals.low_value_type else None,
    )


def _factors(
    input_: PriorityScoringInput,
    config: PriorityScoringConfig,
) -> list[PriorityFactor]:
    signals = input_.signals
    factors = []
    if signals.action_required:
        factors.append(_factor("action_required", config, [signals.id]))
    if signals.deadlines:
        factors.append(_factor("deadline", config, [signals.id]))
    if signals.meeting_details:
        factors.append(_factor("meeting", config, [signals.id]))
    if input_.retrieved_context:
        factors.append(
            _factor("context", config, [item.id for item in input_.retrieved_context])
        )
    if signals.low_value_type:
        factors.append(_factor("low_value", config, [signals.id]))

    for preference in input_.preferences:
        if not preference.enabled or not _matches_preference(input_, preference.value):
            continue
        weight = config.weights["preference"]
        if preference.effect == PreferenceEffect.PENALIZE:
            weight = -weight
        factors.append(
            PriorityFactor(
                name=f"preference:{preference.preference_type.value}",
                direction=_direction(weight),
                weight=weight,
                source_ids=[preference.id],
                details=preference.value,
            )
        )
    return factors or [
        PriorityFactor(
            name="base",
            direction=PriorityFactorDirection.NEUTRAL,
            weight=0,
            source_ids=[signals.id],
        )
    ]


def _factor(
    name: str,
    config: PriorityScoringConfig,
    source_ids: list[str],
) -> PriorityFactor:
    weight = config.weights[name]
    return PriorityFactor(
        name=name,
        direction=_direction(weight),
        weight=weight,
        source_ids=source_ids,
    )


def _direction(weight: float) -> PriorityFactorDirection:
    if weight > 0:
        return PriorityFactorDirection.POSITIVE
    if weight < 0:
        return PriorityFactorDirection.NEGATIVE
    return PriorityFactorDirection.NEUTRAL


def _band(score: float, config: PriorityScoringConfig) -> PriorityBand:
    if score >= config.thresholds["high"]:
        return PriorityBand.HIGH
    if score >= config.thresholds["normal"]:
        return PriorityBand.NORMAL
    return PriorityBand.LOW


def _matches_preference(input_: PriorityScoringInput, value: object) -> bool:
    if not isinstance(value, str):
        return False
    haystack = f"{input_.signals.category} {input_.signals.summary}".lower()
    return value.lower() in haystack
