from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from email_agent.ai import AnalysisService
from email_agent.calendar import create_calendar_proposals
from email_agent.domain import (
    CalendarEventProposal,
    Email,
    EmailAnalysis,
    EmailAnalysisSignals,
    EmailAnalysisStatus,
    PriorityResult,
    ProcessedEmail,
    RetrievedContext,
    UserPreference,
)
from email_agent.logging import get_logger, log_event
from email_agent.preprocessing import normalize_email
from email_agent.priority import (
    PriorityScoringConfig,
    PriorityScoringInput,
    build_priority_explanation,
    score_priority,
)
from email_agent.retrieval import (
    ChromaIndex,
    EmbeddingProvider,
    index_processed_email,
    retrieve_context,
)

logger = get_logger(__name__)


class TriageRepository(Protocol):
    def save_email(self, email: Email) -> None: ...

    def save_processed_email(self, processed_email: ProcessedEmail) -> None: ...

    def save_signals(self, signals: EmailAnalysisSignals) -> None: ...

    def save_priority_result(self, priority_result: PriorityResult) -> None: ...

    def save_context(self, context: RetrievedContext) -> None: ...

    def save_analysis(self, analysis: EmailAnalysis) -> None: ...

    def save_proposal(self, proposal: CalendarEventProposal) -> None: ...

    def list_preferences(self) -> list[UserPreference]: ...


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email_id: str
    processed_email: ProcessedEmail | None = None
    signals: EmailAnalysisSignals | None = None
    retrieved_context: list[RetrievedContext] = []
    priority_result: PriorityResult | None = None
    calendar_proposals: list[CalendarEventProposal] = []
    analysis: EmailAnalysis | None = None
    errors: list[str] = []


def triage_email(
    email: Email,
    repository: TriageRepository,
    analysis_service: AnalysisService,
    *,
    embedding_provider: EmbeddingProvider | None = None,
    index: ChromaIndex | None = None,
    priority_config: PriorityScoringConfig | None = None,
) -> TriageResult:
    log_event(logger, "triage started", email_id=email.id, stage="start")
    repository.save_email(email)
    processed_email = normalize_email(email)
    repository.save_processed_email(processed_email)

    retrieved_context: list[RetrievedContext] = []
    if embedding_provider is not None and index is not None:
        retrieved_context = retrieve_context(
            processed_email,
            embedding_provider,
            index,
            repository=repository,
        )
        log_event(
            logger,
            "retrieval completed",
            email_id=email.id,
            stage="retrieval",
            fields={"retrieved_count": len(retrieved_context)},
        )
        index_processed_email(processed_email, embedding_provider, index)

    analysis_result = analysis_service.analyze(
        processed_email,
        repository,
        context=[item.summary for item in retrieved_context],
    )
    if analysis_result.signals is None:
        log_event(
            logger,
            "analysis failed",
            email_id=email.id,
            stage="analysis",
            fields={"errors": "; ".join(analysis_result.errors)},
        )
        return TriageResult(
            email_id=email.id,
            processed_email=processed_email,
            retrieved_context=retrieved_context,
            errors=analysis_result.errors,
        )

    priority_result = score_priority(
        PriorityScoringInput(
            email_id=email.id,
            signals=analysis_result.signals,
            retrieved_context=retrieved_context,
            preferences=repository.list_preferences(),
        ),
        priority_config,
    )
    repository.save_priority_result(priority_result)
    proposals = create_calendar_proposals(email.id, analysis_result.signals)
    for proposal in proposals:
        repository.save_proposal(proposal)

    analysis = EmailAnalysis(
        id=f"analysis-{email.id}",
        email_id=email.id,
        processed_email_id=processed_email.id,
        signals_id=analysis_result.signals.id,
        priority_result_id=priority_result.id,
        status=EmailAnalysisStatus.COMPLETED,
        calendar_proposal_ids=[proposal.id for proposal in proposals],
        explanation=build_priority_explanation(priority_result),
        completed_at=datetime.now(UTC),
    )
    repository.save_analysis(analysis)
    log_event(
        logger,
        "triage completed",
        email_id=email.id,
        stage="complete",
        fields={
            "priority_band": priority_result.band.value,
            "proposal_count": len(proposals),
        },
    )
    return TriageResult(
        email_id=email.id,
        processed_email=processed_email,
        signals=analysis_result.signals,
        retrieved_context=retrieved_context,
        priority_result=priority_result,
        calendar_proposals=proposals,
        analysis=analysis,
    )


def triage_inbox(
    emails: list[Email],
    repository: TriageRepository,
    analysis_service: AnalysisService,
    *,
    priority_config: PriorityScoringConfig | None = None,
) -> list[TriageResult]:
    results = []
    for email in emails:
        try:
            results.append(
                triage_email(
                    email,
                    repository,
                    analysis_service,
                    priority_config=priority_config,
                )
            )
        except Exception as error:
            results.append(TriageResult(email_id=email.id, errors=[str(error)]))
    return results
