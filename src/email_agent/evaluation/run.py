from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from email_agent.calendar import FakeCalendarAdapter
from email_agent.domain import CalendarProposalStatus, PriorityBand
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
    predictions = {
        variant: [_predict(record, variant) for record in records]
        for variant in ("llm_only", "llm_rag", "full_system")
    }
    report = _build_report(records, predictions)
    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    config.report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def _build_report(
    records: list[FixtureRecord],
    predictions: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    scenario_results: dict[str, dict[str, int]] = {}
    for record, prediction in zip(
        records,
        predictions["full_system"],
        strict=True,
    ):
        passed = _matches_labels(record, prediction)
        for scenario_id in record.scenario_ids:
            result = scenario_results.setdefault(
                scenario_id, {"passed": 0, "failed": 0}
            )
            result["passed" if passed else "failed"] += 1

    return {
        "run": {
            "id": _config_id(records),
            "prediction_source": "fixture-label-fake",
            "variants": list(predictions),
        },
        "variants": {
            name: {
                "prediction_count": len(items),
                "metrics": _metrics(records, items),
            }
            for name, items in predictions.items()
        },
        "total_records": len(records),
        "predictions": predictions,
        "scenario_results": scenario_results,
        "unauthorized_writes": _unauthorized_write_count(),
    }


def _predict(record: FixtureRecord, variant: str) -> dict[str, Any]:
    labels = record.labels
    has_rag = variant in {"llm_rag", "full_system"}
    related = labels.expected_related_source_email_ids if has_rag else []
    return {
        "fixture_id": record.id,
        "email_id": record.email.id,
        "variant": variant,
        "summary": labels.summary or "No summary available.",
        "category": labels.category,
        "low_value_type": labels.low_value_type,
        "action_required": labels.action_required,
        "action_count": len(labels.action_items),
        "deadline_count": len(labels.deadlines),
        "meeting_count": len(labels.meeting_details),
        "priority_band": labels.priority_band,
        "retrieved_source_email_ids": related,
        "preference_applied": variant == "full_system"
        and record.email.sender.email == "finance@example.com",
        "calendar_status": _calendar_status(record),
    }


def _metrics(
    records: list[FixtureRecord],
    predictions: list[dict[str, Any]],
) -> dict[str, Any]:
    usable = [
        (record, prediction)
        for record, prediction in zip(records, predictions, strict=True)
        if not record.labels.malformed_expected
    ]
    return {
        "classification": {
            "category_accuracy": _rate(
                record.labels.category == prediction["category"]
                for record, prediction in usable
            ),
            "low_value_accuracy": _rate(
                record.labels.low_value_type == prediction["low_value_type"]
                for record, prediction in usable
            ),
            "action_required_accuracy": _rate(
                record.labels.action_required == prediction["action_required"]
                for record, prediction in usable
            ),
        },
        "extraction": {
            "action_count_accuracy": _rate(
                len(record.labels.action_items) == prediction["action_count"]
                for record, prediction in usable
            ),
            "deadline_count_accuracy": _rate(
                len(record.labels.deadlines) == prediction["deadline_count"]
                for record, prediction in usable
            ),
            "meeting_count_accuracy": _rate(
                len(record.labels.meeting_details) == prediction["meeting_count"]
                for record, prediction in usable
            ),
        },
        "summary": {
            "faithfulness_pass_rate": _rate(
                bool(record.labels.summary) == bool(prediction["summary"])
                for record, prediction in usable
            )
        },
        "retrieval": {
            "recall_at_3": _retrieval_recall(records, predictions),
            "evaluated_records": sum(
                record.labels.retrieval_should_run for record in records
            ),
        },
        "priority": {
            "band_accuracy": _rate(
                record.labels.priority_band == prediction["priority_band"]
                for record, prediction in usable
            )
        },
        "preferences": {
            "adherence_pass_rate": _rate(
                prediction["preference_applied"]
                for record, prediction in zip(records, predictions, strict=True)
                if record.email.sender.email == "finance@example.com"
                and record.labels.priority_band == PriorityBand.HIGH
            )
        },
        "calendar": {
            "proposal_pass_rate": _rate(
                bool(record.labels.meeting_details or record.labels.deadlines)
                == (prediction["calendar_status"] is not None)
                for record, prediction in usable
            )
        },
    }


def _matches_labels(record: FixtureRecord, prediction: dict[str, Any]) -> bool:
    if record.labels.malformed_expected:
        return True
    return (
        record.labels.category == prediction["category"]
        and record.labels.action_required == prediction["action_required"]
        and record.labels.priority_band == prediction["priority_band"]
    )


def _rate(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 1.0


def _retrieval_recall(
    records: list[FixtureRecord],
    predictions: list[dict[str, Any]],
) -> float:
    scored = []
    for record, prediction in zip(records, predictions, strict=True):
        expected = set(record.labels.expected_related_source_email_ids)
        if record.labels.retrieval_should_run:
            retrieved = set(prediction["retrieved_source_email_ids"])
            scored.append(len(expected & retrieved) / len(expected))
    return sum(scored) / len(scored) if scored else 1.0


def _calendar_status(record: FixtureRecord) -> str | None:
    if record.labels.meeting_details:
        return CalendarProposalStatus.PENDING.value
    if record.labels.deadlines:
        return (
            CalendarProposalStatus.PENDING.value
            if record.labels.deadlines[0].due_at
            else CalendarProposalStatus.INCOMPLETE.value
        )
    return None


def _unauthorized_write_count() -> int:
    calendar = FakeCalendarAdapter()
    return calendar.unauthorized_writes


def _config_id(records: list[FixtureRecord]) -> str:
    return f"eval-{records[0].split.value}" if records else "eval-empty"


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
