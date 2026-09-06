from pathlib import Path

from fastapi.testclient import TestClient

from email_agent.api import create_app
from email_agent.config import Settings


def settings(tmp_path: Path) -> Settings:
    return Settings(
        **{"_env_file": None, "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}"}
    )


def test_api_imports_and_processes_fixture_inbox(tmp_path: Path) -> None:
    client = TestClient(create_app(settings=settings(tmp_path)))

    imported = client.post(
        "/imports/fixtures",
        json={"path": "datasets/fixtures/dev.jsonl"},
    )
    processed = client.post("/processing/inbox", json={})

    assert imported.status_code == 200
    assert imported.json()["imported"] == 8
    assert processed.status_code == 200
    assert len(processed.json()) == 8
    assert any(item["priority_result"] for item in processed.json())
