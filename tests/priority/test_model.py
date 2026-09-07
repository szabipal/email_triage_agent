from email_agent.domain import EmailAnalysisSignals
from email_agent.priority import PriorityScoringInput


def test_priority_scoring_input_serializes_decision_inputs() -> None:
    signals = EmailAnalysisSignals(
        id="signals-1",
        processed_email_id="processed-1",
        summary="Ada asks for review.",
        category="work",
        action_required=True,
        low_value_type=None,
        confidence=0.9,
    )

    restored = PriorityScoringInput.model_validate_json(
        PriorityScoringInput(email_id="email-1", signals=signals).model_dump_json()
    )

    assert restored.email_id == "email-1"
    assert restored.signals.id == "signals-1"
