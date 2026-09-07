from pathlib import Path

from fastapi.testclient import TestClient

from email_agent.api import create_app
from email_agent.config import Settings


def settings(tmp_path: Path) -> Settings:
    return Settings(
        **{"_env_file": None, "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}"}
    )


def processed_client(tmp_path: Path) -> TestClient:
    client = TestClient(create_app(settings=settings(tmp_path)))
    client.post("/imports/fixtures", json={"path": "datasets/fixtures/dev.jsonl"})
    client.post("/processing/inbox", json={})
    return client


def test_inbox_endpoint_returns_priority_sorted_items(tmp_path: Path) -> None:
    response = processed_client(tmp_path).get("/inbox")

    assert response.status_code == 200
    items = response.json()
    assert items[0]["priority_score"] >= items[-1]["priority_score"]
    assert {"summary", "category", "action_required"} <= set(items[0])


def test_email_detail_endpoint_returns_factors_context_and_proposals(
    tmp_path: Path,
) -> None:
    response = processed_client(tmp_path).get("/emails/email-dev-003")

    assert response.status_code == 200
    detail = response.json()
    assert detail["email"]["id"] == "email-dev-003"
    assert detail["factors"]
    assert detail["proposals"]
