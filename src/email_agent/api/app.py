from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from email_agent.ai import AnalysisService, FakeLLMProvider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.config import Settings, load_settings
from email_agent.evaluation.validator import validate_fixture_file
from email_agent.ingestion import import_fixture_emails
from email_agent.orchestration import TriageResult, triage_email, triage_inbox
from email_agent.persistence import make_session_factory
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository
from email_agent.preprocessing import normalize_email


class HealthResponse(BaseModel):
    status: Literal["ok"]


class ImportRequest(BaseModel):
    path: Path


class ImportResponse(BaseModel):
    imported: int


class ProcessRequest(BaseModel):
    email_ids: list[str] | None = None


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    session_factory = make_session_factory(resolved_settings)

    app = FastAPI(title="Email Agent API", version="0.1.0")

    def get_settings() -> Settings:
        return resolved_settings

    @app.get("/health", response_model=HealthResponse)
    def health(
        _settings: Annotated[Settings, Depends(get_settings)],
    ) -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/imports/fixtures", response_model=ImportResponse)
    def import_fixtures(request: ImportRequest) -> ImportResponse:
        _init_db(session_factory)
        with session_factory.begin() as session:
            imported = import_fixture_emails(
                request.path,
                SqlAlchemyRepository(session),
            )
        return ImportResponse(imported=len(imported))

    @app.post("/processing/inbox", response_model=list[TriageResult])
    def process_inbox(request: ProcessRequest) -> list[TriageResult]:
        _init_db(session_factory)
        with session_factory.begin() as session:
            repository = SqlAlchemyRepository(session)
            emails = repository.list_emails()
            if request.email_ids is not None:
                emails = [email for email in emails if email.id in request.email_ids]
            return triage_inbox(
                emails,
                repository,
                _fixture_analysis_service(emails),
            )

    @app.post("/processing/emails/{email_id}", response_model=TriageResult)
    def process_email(email_id: str) -> TriageResult:
        _init_db(session_factory)
        with session_factory.begin() as session:
            repository = SqlAlchemyRepository(session)
            email = repository.get_email(email_id)
            if email is None:
                return TriageResult(email_id=email_id, errors=["email not found"])
            return triage_email(email, repository, _fixture_analysis_service([email]))

    return app


def _init_db(session_factory) -> None:
    from email_agent.persistence.models import Base

    Base.metadata.create_all(session_factory.kw["bind"])


def _fixture_analysis_service(emails) -> AnalysisService:
    by_id = {
        record.email.id: record
        for record in validate_fixture_file(Path("datasets/fixtures/dev.jsonl"))
    }
    outputs = {}
    for email in emails:
        if email.id not in by_id or not email.body_raw.strip():
            continue
        processed = normalize_email(email)
        labels = by_id[email.id].labels
        outputs[render_analysis_prompt(processed, output_language="en")] = {
            "id": f"signals-{email.id}",
            "processed_email_id": processed.id,
            "summary": labels.summary or "No summary available.",
            "category": labels.category,
            "action_required": labels.action_required,
            "low_value_type": labels.low_value_type,
            "confidence": 0.9,
            "action_items": [
                item.model_dump(mode="json") for item in labels.action_items
            ],
            "deadlines": [item.model_dump(mode="json") for item in labels.deadlines],
            "meeting_details": [
                item.model_dump(mode="json") for item in labels.meeting_details
            ],
        }
    return AnalysisService(FakeLLMProvider(outputs))
