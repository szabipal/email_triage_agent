from pathlib import Path

from fastapi.testclient import TestClient

from email_agent.api import create_app
from email_agent.config import Settings


def settings(tmp_path: Path) -> Settings:
    return Settings(
        **{"_env_file": None, "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}"}
    )


def test_preference_endpoints_upsert_and_list_preferences(tmp_path: Path) -> None:
    client = TestClient(create_app(settings=settings(tmp_path)))
    payload = {
        "id": "ignored",
        "preference_type": "category",
        "value": "finance",
        "effect": "boost",
        "weight": 1,
        "enabled": True,
    }

    saved = client.put("/preferences/pref-1", json=payload)
    listed = client.get("/preferences")

    assert saved.status_code == 200
    assert saved.json()["id"] == "pref-1"
    assert listed.json()[0]["value"] == "finance"
