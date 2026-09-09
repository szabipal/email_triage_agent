from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from email_agent.ai import LLMResponse
from email_agent.api import create_app
from email_agent.config import Settings
from email_agent.domain import Email, EmailIdentity, EmailSource


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


def test_api_syncs_gmail_and_caps_llm_body(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts: list[str] = []

    def fake_import_gmail_unread(repository, **kwargs):
        email = Email(
            id="gmail-email-1",
            provider_message_id="gmail:1",
            subject="Unread invoice",
            sender=EmailIdentity(email="billing@example.test"),
            recipients=[EmailIdentity(email="user@example.test")],
            received_at=datetime(2026, 1, 1, tzinfo=UTC),
            body_raw="abcdef",
            source=EmailSource.GMAIL,
        )
        repository.save_email(email)
        return [email]

    def fake_complete(self, request):
        prompts.append(request.prompt)
        return LLMResponse(
            output={
                "id": "signals-gmail",
                "processed_email_id": "processed-gmail-email-1",
                "summary": "Billing asks for payment.",
                "category": "billing_payment_issue",
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
        "email_agent.api.app.import_gmail_unread", fake_import_gmail_unread
    )
    monkeypatch.setattr(
        "email_agent.ai.real.OpenAILLMProvider.complete_structured",
        fake_complete,
    )
    client = TestClient(
        create_app(
            settings(
                tmp_path,
                llm_provider="openai",
                llm_model="gpt-test",
                llm_api_key="test-key",  # allow-secret
                gmail_credentials_path=tmp_path / "credentials.json",
                llm_max_body_chars=3,
            )
        )
    )

    response = client.post("/sync/gmail", json={})

    assert response.status_code == 200
    assert response.json() == {"imported": 1, "processed": 1, "errors": []}
    assert "Body: abc\n[truncated]" in prompts[0]
    assert client.get("/inbox").json()[0]["email_id"] == "gmail-email-1"


def test_api_gmail_sync_requires_credentials_path(tmp_path: Path) -> None:
    client = TestClient(create_app(settings(tmp_path)))

    response = client.post("/sync/gmail", json={})

    assert response.status_code == 400
    assert "EMAIL_AGENT_GMAIL_CREDENTIALS_PATH" in response.text
