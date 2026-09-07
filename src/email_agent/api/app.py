from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from email_agent.ai import AnalysisService, FakeLLMProvider, make_llm_provider
from email_agent.ai.prompts import render_analysis_prompt
from email_agent.api.schemas import ApiError, EmailDetail, InboxItem
from email_agent.calendar import (
    CalendarPort,
    FakeCalendarAdapter,
    GoogleCalendarAdapter,
    decide_proposal,
    execute_approved_proposal,
)
from email_agent.config import Settings, load_settings
from email_agent.domain import (
    ApprovalDecision,
    CalendarEventProposal,
    ToolApproval,
    UserPreference,
)
from email_agent.evaluation.validator import validate_fixture_file
from email_agent.ingestion import import_eml_emails, import_fixture_emails
from email_agent.orchestration import TriageResult, triage_email, triage_inbox
from email_agent.persistence import make_session_factory
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository
from email_agent.preprocessing import normalize_email


class HealthResponse(BaseModel):
    status: Literal["ok"]


class ImportRequest(BaseModel):
    path: Path


class EmlImportRequest(BaseModel):
    paths: list[Path]
    limit: int = 5


class ImportResponse(BaseModel):
    imported: int


class ProcessRequest(BaseModel):
    email_ids: list[str] | None = None


class ApprovalRequest(BaseModel):
    decision: ApprovalDecision
    decided_by: str
    approval_notes: str | None = None


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    session_factory = make_session_factory(resolved_settings)
    calendar_adapter: CalendarPort = _calendar_adapter(resolved_settings)

    app = FastAPI(title="Email Agent API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    @app.post("/imports/eml", response_model=ImportResponse)
    def import_eml(request: EmlImportRequest) -> ImportResponse:
        _init_db(session_factory)
        with session_factory.begin() as session:
            imported = import_eml_emails(
                request.paths,
                SqlAlchemyRepository(session),
                limit=request.limit,
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
                _analysis_service(resolved_settings, emails),
            )

    @app.post("/processing/emails/{email_id}", response_model=TriageResult)
    def process_email(email_id: str) -> TriageResult:
        _init_db(session_factory)
        with session_factory.begin() as session:
            repository = SqlAlchemyRepository(session)
            email = repository.get_email(email_id)
            if email is None:
                return TriageResult(email_id=email_id, errors=["email not found"])
            return triage_email(
                email,
                repository,
                _analysis_service(resolved_settings, [email]),
            )

    @app.get("/inbox", response_model=list[InboxItem])
    def inbox() -> list[InboxItem]:
        _init_db(session_factory)
        with session_factory() as session:
            repository = SqlAlchemyRepository(session)
            items = [
                _inbox_item(repository, analysis)
                for analysis in repository.list_analyses()
            ]
        return sorted(items, key=lambda item: item.priority_score, reverse=True)

    @app.get(
        "/emails/{email_id}",
        response_model=EmailDetail,
        responses={404: {"model": ApiError}},
    )
    def email_detail(email_id: str):
        _init_db(session_factory)
        with session_factory() as session:
            repository = SqlAlchemyRepository(session)
            analysis = repository.get_analysis_for_email(email_id)
            email = repository.get_email(email_id)
            if analysis is None or email is None:
                return {"code": "not_found", "message": "email not found"}
            priority = repository.get_priority_result(analysis.priority_result_id)
            return EmailDetail(
                email=email,
                analysis=analysis,
                factors=priority.factors if priority else [],
                retrieved_context=repository.list_context_for_email(email_id),
                proposals=repository.list_proposals_for_email(email_id),
            )

    @app.get("/preferences", response_model=list[UserPreference])
    def list_preferences() -> list[UserPreference]:
        _init_db(session_factory)
        with session_factory() as session:
            return SqlAlchemyRepository(session).list_preferences()

    @app.put("/preferences/{preference_id}", response_model=UserPreference)
    def upsert_preference(
        preference_id: str,
        preference: UserPreference,
    ) -> UserPreference:
        _init_db(session_factory)
        saved = preference.model_copy(update={"id": preference_id})
        with session_factory.begin() as session:
            SqlAlchemyRepository(session).save_preference(saved)
        return saved

    @app.get("/proposals", response_model=list[CalendarEventProposal])
    def list_proposals() -> list[CalendarEventProposal]:
        _init_db(session_factory)
        with session_factory() as session:
            return SqlAlchemyRepository(session).list_proposals()

    @app.post(
        "/proposals/{proposal_id}/approval",
        response_model=ToolApproval,
        responses={404: {"model": ApiError}},
    )
    def record_proposal_decision(
        proposal_id: str,
        request: ApprovalRequest,
    ) -> ToolApproval:
        _init_db(session_factory)
        with session_factory.begin() as session:
            repository = SqlAlchemyRepository(session)
            proposal = repository.get_proposal(proposal_id)
            if proposal is None:
                raise HTTPException(status_code=404, detail="proposal not found")
            try:
                proposal, approval = decide_proposal(
                    proposal,
                    request.decision,
                    decided_by=request.decided_by,
                    approval_notes=request.approval_notes,
                )
            except ValueError as error:
                raise HTTPException(status_code=409, detail=str(error)) from error
            repository.save_proposal(proposal)
            repository.save_approval(approval)
            return approval

    @app.post(
        "/proposals/{proposal_id}/execute",
        response_model=CalendarEventProposal,
        responses={403: {"model": ApiError}, 404: {"model": ApiError}},
    )
    def execute_proposal(proposal_id: str) -> CalendarEventProposal:
        _init_db(session_factory)
        with session_factory.begin() as session:
            repository = SqlAlchemyRepository(session)
            try:
                return execute_approved_proposal(
                    proposal_id,
                    repository,
                    calendar_adapter,
                )
            except LookupError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error
            except PermissionError as error:
                raise HTTPException(status_code=403, detail=str(error)) from error
            except RuntimeError as error:
                raise HTTPException(status_code=502, detail=str(error)) from error

    return app


def _calendar_adapter(settings: Settings) -> CalendarPort:
    if settings.calendar_provider == "google" and settings.calendar_execution_enabled:
        if settings.google_calendar_credentials_path is None:
            raise ValueError("Google Calendar credentials path is required")
        return GoogleCalendarAdapter(settings.google_calendar_credentials_path)
    return FakeCalendarAdapter()


def _inbox_item(repository: SqlAlchemyRepository, analysis) -> InboxItem:
    email = repository.get_email(analysis.email_id)
    signals = repository.get_signals(analysis.signals_id)
    priority = repository.get_priority_result(analysis.priority_result_id)
    assert email is not None and signals is not None and priority is not None
    return InboxItem(
        email_id=email.id,
        subject=email.subject,
        sender=email.sender.email,
        received_at=email.received_at,
        summary=signals.summary,
        category=signals.category,
        action_required=signals.action_required,
        priority_band=priority.band,
        priority_score=priority.score,
    )


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


def _analysis_service(settings: Settings, emails) -> AnalysisService:
    if settings.llm_provider == "fake":
        return _fixture_analysis_service(emails)
    return AnalysisService(
        make_llm_provider(settings),
        model=settings.llm_model,
        output_language=settings.output_language,
    )
