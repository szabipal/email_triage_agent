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


def test_proposal_endpoints_list_and_record_rejection(tmp_path: Path) -> None:
    client = processed_client(tmp_path)
    proposals = client.get("/proposals").json()
    proposal_id = proposals[0]["id"]

    response = client.post(
        f"/proposals/{proposal_id}/approval",
        json={"decision": "rejected", "decided_by": "user"},
    )

    assert response.status_code == 200
    assert response.json()["proposal_id"] == proposal_id
    assert response.json()["decision"] == "rejected"


def test_proposal_execution_requires_approval_and_is_idempotent(
    tmp_path: Path,
) -> None:
    client = processed_client(tmp_path)
    proposal_id = client.get("/proposals").json()[0]["id"]

    unapproved = client.post(f"/proposals/{proposal_id}/execute")
    assert unapproved.status_code == 403

    approval = client.post(
        f"/proposals/{proposal_id}/approval",
        json={"decision": "approved", "decided_by": "user"},
    )
    assert approval.status_code == 200

    first = client.post(f"/proposals/{proposal_id}/execute")
    second = client.post(f"/proposals/{proposal_id}/execute")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "executed"
    assert first.json()["provider_event_id"] == second.json()["provider_event_id"]
