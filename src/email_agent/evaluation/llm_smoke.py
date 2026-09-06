from __future__ import annotations

import json
from pathlib import Path

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.evaluation.fixtures import DatasetSplit, FixtureRecord
from email_agent.evaluation.validator import validate_fixture_file
from email_agent.preprocessing import normalize_email


def run_llm_analysis_smoke(
    dataset_path: Path,
    predictions_path: Path,
    *,
    expected_split: DatasetSplit = DatasetSplit.DEV,
    limit: int = 3,
) -> list[dict[str, object]]:
    records = [
        record
        for record in validate_fixture_file(dataset_path, expected_split=expected_split)
        if not record.labels.malformed_expected
    ][:limit]
    processed = [normalize_email(record.email) for record in records]
    outputs = {
        render_analysis_prompt(item, output_language="en"): _output(record, item.id)
        for record, item in zip(records, processed, strict=True)
    }
    service = AnalysisService(FakeLLMProvider(outputs))
    predictions = []

    for record, item in zip(records, processed, strict=True):
        result = service.analyze(item)
        assert result.signals is not None
        predictions.append(
            {
                "fixture_id": record.id,
                "email_id": record.email.id,
                "signals": result.signals.model_dump(mode="json"),
            }
        )

    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions_path.write_text(
        json.dumps(predictions, indent=2, sort_keys=True) + "\n"
    )
    return predictions


def _output(record: FixtureRecord, processed_email_id: str) -> dict[str, object]:
    labels = record.labels
    return {
        "id": f"signals-{record.email.id}",
        "processed_email_id": processed_email_id,
        "summary": labels.summary or "No summary available.",
        "category": labels.category,
        "action_required": labels.action_required,
        "low_value_type": labels.low_value_type,
        "confidence": 0.9,
        "action_items": [item.model_dump(mode="json") for item in labels.action_items],
        "deadlines": [item.model_dump(mode="json") for item in labels.deadlines],
        "meeting_details": [
            item.model_dump(mode="json") for item in labels.meeting_details
        ],
        "source_language": None,
        "output_language": "en",
    }
