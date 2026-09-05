from pathlib import Path

import pytest

from email_agent.evaluation import DatasetSplit, DatasetValidationError
from email_agent.evaluation.validator import validate_fixture_file


def test_validator_accepts_dev_fixture_file() -> None:
    records = validate_fixture_file(
        Path("datasets/fixtures/dev.jsonl"),
        expected_split=DatasetSplit.DEV,
    )

    assert records


def test_validator_reports_invalid_jsonl_line(tmp_path: Path) -> None:
    fixture_file = tmp_path / "bad.jsonl"
    fixture_file.write_text("{not-json}\n")

    with pytest.raises(DatasetValidationError, match="bad.jsonl:1"):
        validate_fixture_file(fixture_file)


def test_validator_reports_missing_related_source(tmp_path: Path) -> None:
    fixture_file = tmp_path / "missing-source.jsonl"
    fixture_file.write_text(
        Path("datasets/fixtures/dev.jsonl")
        .read_text()
        .splitlines()[-1]
        .replace(
            "email-dev-007",
            "missing-email",
        )
        + "\n"
    )

    with pytest.raises(DatasetValidationError, match="missing source email ids"):
        validate_fixture_file(fixture_file, expected_split=DatasetSplit.DEV)
