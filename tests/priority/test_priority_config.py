import pytest
from pydantic import ValidationError

from email_agent.config import Settings
from email_agent.priority import PriorityScoringConfig, load_priority_config


def test_priority_config_loads_default_and_overridden_weights() -> None:
    config = load_priority_config(
        Settings(
            **{
                "_env_file": None,
                "priority_weights": {"action_required": 40.0},
            }
        )
    )

    assert config.weights["action_required"] == 40.0
    assert config.weights["low_value"] < 0


def test_priority_config_rejects_unknown_weight() -> None:
    with pytest.raises(ValidationError, match="unknown priority weights"):
        PriorityScoringConfig(weights={"made_up": 1.0})
