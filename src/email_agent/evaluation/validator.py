from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from pydantic import ValidationError

from email_agent.evaluation.fixtures import DatasetSplit, FixtureRecord


class DatasetValidationError(ValueError):
    pass


def load_fixture_records(path: Path) -> list[FixtureRecord]:
    records: list[FixtureRecord] = []
    errors: list[str] = []

    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line:
            continue

        try:
            records.append(FixtureRecord.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValidationError) as error:
            errors.append(f"{path}:{line_number}: {error}")

    if errors:
        raise DatasetValidationError("\n".join(errors))

    return records


def validate_fixture_file(
    path: Path,
    *,
    expected_split: DatasetSplit | None = None,
) -> list[FixtureRecord]:
    records = load_fixture_records(path)
    _validate_records(records, expected_split=expected_split)
    return records


def _validate_records(
    records: Iterable[FixtureRecord],
    *,
    expected_split: DatasetSplit | None,
) -> None:
    records = list(records)
    fixture_ids = _find_duplicates(record.id for record in records)
    email_ids = _find_duplicates(record.email.id for record in records)
    errors: list[str] = []

    if fixture_ids:
        errors.append(f"duplicate fixture ids: {', '.join(fixture_ids)}")

    if email_ids:
        errors.append(f"duplicate email ids: {', '.join(email_ids)}")

    if expected_split is not None:
        wrong_split = [
            record.id for record in records if record.split != expected_split
        ]
        if wrong_split:
            errors.append(
                f"records outside {expected_split.value} split: "
                + ", ".join(wrong_split)
            )

    known_email_ids = {record.email.id for record in records}
    for record in records:
        missing_sources = [
            source_id
            for source_id in record.labels.expected_related_source_email_ids
            if source_id not in known_email_ids
        ]
        if missing_sources:
            errors.append(
                f"{record.id} references missing source email ids: "
                + ", ".join(missing_sources)
            )

    if errors:
        raise DatasetValidationError("\n".join(errors))


def _find_duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)

    return sorted(duplicates)
