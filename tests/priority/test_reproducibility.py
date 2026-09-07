from datetime import UTC, datetime
from inspect import signature

from email_agent.domain import EmailAnalysisSignals
from email_agent.priority import PriorityScoringInput, score_priority


def test_priority_scoring_is_reproducible_for_same_inputs() -> None:
    input_ = PriorityScoringInput(
        email_id="email-1",
        signals=EmailAnalysisSignals(
            id="signals-1",
            processed_email_id="processed-1",
            summary="Ada asks for review.",
            category="work",
            action_required=True,
            low_value_type=None,
            confidence=0.9,
        ),
    )
    now = datetime(2026, 1, 1, tzinfo=UTC)

    first = score_priority(input_, calculated_at=now)
    second = score_priority(input_, calculated_at=now)

    assert first == second


def test_priority_scoring_has_no_llm_provider_dependency() -> None:
    assert "provider" not in signature(score_priority).parameters
