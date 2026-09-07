from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from email_agent.ai import LLMResponse
from email_agent.api import create_app
from email_agent.config import Settings


def settings(tmp_path: Path, **values: object) -> Settings:
    return Settings(
        **{
            "_env_file": None,
            "database_url": f"sqlite:///{tmp_path / 'db.sqlite'}",
            **values,
        }
    )


def test_api_imports_eml_file(tmp_path: Path) -> None:
    path = tmp_path / "message.eml"
    path.write_text(
        "Message-ID: <real-1@example.test>\n"
        "From: ada@example.test\n"
        "To: user@example.test\n"
        "Subject: Review\n\n"
        "Please review this today."
    )
    client = TestClient(create_app(settings(tmp_path)))

    response = client.post("/imports/eml", json={"paths": [str(path)]})

    assert response.status_code == 200
    assert response.json() == {"imported": 1}


def test_api_openai_mode_requires_key(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="EMAIL_AGENT_LLM_API_KEY"):
        settings(tmp_path, llm_provider="openai")


def test_api_processes_eml_with_configured_openai_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_models: list[str] = []

    def fake_complete(self, request):
        seen_models.append(request.model)
        return LLMResponse(
            output={
                "id": "signals-eml",
                "processed_email_id": "processed-eml",
                "summary": "Ada asks for review.",
                "category": "work",
                "action_required": True,
                "low_value_type": None,
                "confidence": 0.9,
                "action_items": [],
                "deadlines": [],
                "meeting_details": [],
            },
            model_name=request.model,
            prompt_version=request.prompt_version,
            schema_version=request.schema_name,
        )

    monkeypatch.setattr(
        "email_agent.ai.real.OpenAILLMProvider.complete_structured",
        fake_complete,
    )
    path = tmp_path / "message.eml"
    path.write_text(
        "Message-ID: <real-1@example.test>\n"
        "From: ada@example.test\n"
        "To: user@example.test\n"
        "Subject: Review\n\n"
        "Please review this today."
    )
    client = TestClient(
        create_app(
            settings(
                tmp_path,
                llm_provider="openai",
                llm_model="gpt-test",
                llm_api_key="test-key",  # allow-secret
            )
        )
    )
    client.post("/imports/eml", json={"paths": [str(path)]})

    response = client.post("/processing/inbox", json={})

    assert response.status_code == 200
    assert response.json()[0]["analysis"]["status"] == "completed"
    assert seen_models == ["gpt-test"]
