from pathlib import Path

from fastapi.testclient import TestClient

from email_agent.api import create_app
from email_agent.config import Settings


def test_fake_provider_flow_imports_processes_displays_and_executes(
    tmp_path: Path,
) -> None:
    client = TestClient(
        create_app(
            Settings(
                **{
                    "_env_file": None,
                    "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}",
                }
            )
        )
    )

    assert (
        client.post(
            "/imports/fixtures",
            json={"path": "datasets/fixtures/dev.jsonl"},
        ).json()["imported"]
        >= 1
    )
    assert client.post("/processing/inbox", json={}).status_code == 200

    inbox = client.get("/inbox").json()
    assert inbox[0]["priority_score"] >= inbox[-1]["priority_score"]

    detail = client.get(f"/emails/{inbox[0]['email_id']}").json()
    assert detail["analysis"]["explanation"]

    proposal = client.get("/proposals").json()[0]
    assert client.post(f"/proposals/{proposal['id']}/execute").status_code == 403
    assert (
        client.post(
            f"/proposals/{proposal['id']}/approval",
            json={"decision": "approved", "decided_by": "user"},
        ).status_code
        == 200
    )
    executed = client.post(f"/proposals/{proposal['id']}/execute").json()
    assert executed["status"] == "executed"
    assert executed["provider_event_id"]
