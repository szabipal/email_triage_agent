from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from email_agent.domain import PriorityBand
from email_agent.evaluation.fixtures import DatasetSplit, FixtureRecord
from email_agent.evaluation.validator import validate_fixture_file


class EvalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_path: Path
    report_path: Path
    expected_split: DatasetSplit = DatasetSplit.DEV


def run_evaluation(config: EvalConfig) -> dict[str, Any]:
    records = validate_fixture_file(
        config.dataset_path,
        expected_split=config.expected_split,
    )
    report = _build_report(records)
    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    config.report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def _build_report(records: list[FixtureRecord]) -> dict[str, Any]:
    scenario_results: dict[str, dict[str, int]] = {}

    for record in records:
        passed = _baseline_passes(record)
        for scenario_id in record.scenario_ids:
            result = scenario_results.setdefault(
                scenario_id, {"passed": 0, "failed": 0}
            )
            result["passed" if passed else "failed"] += 1

    return {
        "baseline": "empty",
        "total_records": len(records),
        "scenario_results": scenario_results,
    }


def _baseline_passes(record: FixtureRecord) -> bool:
    return (
        record.labels.category == "unknown"
        and not record.labels.action_required
        and record.labels.priority_band == PriorityBand.NORMAL
    )


def load_config(path: Path) -> EvalConfig:
    return EvalConfig.model_validate_json(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    report = run_evaluation(load_config(args.config))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
