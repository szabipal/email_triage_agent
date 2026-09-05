import json
from pathlib import Path

from email_agent.evaluation import FixtureRecord

DEV_FIXTURES = Path("datasets/fixtures/dev.jsonl")


def load_dev_fixtures() -> list[FixtureRecord]:
    return [
        FixtureRecord.model_validate(json.loads(line))
        for line in DEV_FIXTURES.read_text().splitlines()
        if line
    ]


def test_dev_fixture_inbox_validates() -> None:
    records = load_dev_fixtures()

    assert len(records) >= 6
    assert all(record.split == "dev" for record in records)


def test_dev_fixture_inbox_has_required_initial_scenarios() -> None:
    records = load_dev_fixtures()
    scenarios = {scenario for record in records for scenario in record.scenario_ids}
    non_english = [
        record
        for record in records
        if "multilingual" in record.scenario_ids and record.labels.supported_language
    ]

    assert {"low-value", "action", "deadline", "meeting", "malformed"} <= scenarios
    assert len(non_english) >= 2
