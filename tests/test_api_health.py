from fastapi.testclient import TestClient

from email_agent.api import create_app
from email_agent.config import Settings


def build_settings(**values: object) -> Settings:
    return Settings(**{"_env_file": None, **values})


def test_health_endpoint_returns_stable_ok_response() -> None:
    app = create_app(settings=build_settings(environment="test"))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
