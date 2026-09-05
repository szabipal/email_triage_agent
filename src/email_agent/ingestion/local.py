from __future__ import annotations

from pathlib import Path

from email_agent.domain import Email
from email_agent.evaluation import validate_fixture_file


def load_fixture_emails(path: Path) -> list[Email]:
    return [record.email for record in validate_fixture_file(path)]
