from datetime import UTC, datetime

from email_agent.domain import (
    EmailAnalysisSignals,
    LowValueType,
    PreferenceEffect,
    PreferenceType,
    PriorityBand,
    UserPreference,
)
from email_agent.priority import PriorityScoringInput, score_priority

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def signals(**updates: object) -> EmailAnalysisSignals:
    data = {
        "id": "signals-1",
        "processed_email_id": "processed-1",
        "summary": "Ada asks for review.",
        "category": "work",
        "action_required": False,
        "low_value_type": None,
        "confidence": 0.9,
    } | updates
    return EmailAnalysisSignals.model_validate(data)


def test_priority_scoring_maps_core_signal_cases_to_bands() -> None:
    cases = [
        (signals(action_required=True), PriorityBand.HIGH),
        (signals(low_value_type=LowValueType.NEWSLETTER), PriorityBand.LOW),
        (signals(), PriorityBand.NORMAL),
    ]

    assert [
        score_priority(
            PriorityScoringInput(email_id=f"email-{index}", signals=item),
            calculated_at=NOW,
        ).band
        for index, (item, _) in enumerate(cases)
    ] == [expected for _, expected in cases]


def test_priority_scoring_applies_matching_preference() -> None:
    result = score_priority(
        PriorityScoringInput(
            email_id="email-1",
            signals=signals(category="finance", summary="Invoice approval"),
            preferences=[
                UserPreference(
                    id="pref-1",
                    preference_type=PreferenceType.CATEGORY,
                    value="finance",
                    effect=PreferenceEffect.BOOST,
                    weight=1,
                    enabled=True,
                )
            ],
        ),
        calculated_at=NOW,
    )

    assert result.score == 50
    assert result.preference_matches == ["pref-1"]
