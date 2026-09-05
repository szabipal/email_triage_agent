from __future__ import annotations

from sqlalchemy.orm import Session

from email_agent.domain import (
    CalendarEventProposal,
    Email,
    EmailAnalysis,
    EmailAnalysisSignals,
    PriorityResult,
    ProcessedEmail,
    ProposedAction,
    RetrievedContext,
    ToolApproval,
    UserPreference,
)
from email_agent.persistence.models import (
    AnalysisSignalsRecord,
    CalendarEventProposalRecord,
    EmailAnalysisRecord,
    EmailRecord,
    PriorityResultRecord,
    ProcessedEmailRecord,
    ProposedActionRecord,
    RetrievedContextRecord,
    ToolApprovalRecord,
    UserPreferenceRecord,
)


class SqlAlchemyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_email(self, email: Email) -> None:
        payload = email.model_dump(mode="json")
        self.session.merge(
            EmailRecord(
                id=email.id,
                provider_message_id=email.provider_message_id,
                subject=email.subject,
                sender=payload["sender"],
                recipients=payload["recipients"],
                received_at=email.received_at,
                body_raw=email.body_raw,
                source=email.source.value,
                payload=payload,
            )
        )

    def get_email(self, email_id: str) -> Email | None:
        record = self.session.get(EmailRecord, email_id)
        return Email.model_validate(record.payload) if record else None

    def save_processed_email(self, processed_email: ProcessedEmail) -> None:
        self.session.merge(
            ProcessedEmailRecord(
                id=processed_email.id,
                email_id=processed_email.email_id,
                status=processed_email.status.value,
                normalized_subject=processed_email.normalized_subject,
                normalized_body=processed_email.normalized_body,
                processed_at=processed_email.processed_at,
                payload=processed_email.model_dump(mode="json"),
            )
        )

    def save_signals(self, signals: EmailAnalysisSignals) -> None:
        self.session.merge(
            AnalysisSignalsRecord(
                id=signals.id,
                processed_email_id=signals.processed_email_id,
                category=signals.category,
                action_required=signals.action_required,
                confidence=signals.confidence,
                payload=signals.model_dump(mode="json"),
            )
        )

    def save_analysis(self, analysis: EmailAnalysis) -> None:
        self.session.merge(
            EmailAnalysisRecord(
                id=analysis.id,
                email_id=analysis.email_id,
                processed_email_id=analysis.processed_email_id,
                signals_id=analysis.signals_id,
                priority_result_id=analysis.priority_result_id,
                status=analysis.status.value,
                payload=analysis.model_dump(mode="json"),
            )
        )

    def get_analysis(self, analysis_id: str) -> EmailAnalysis | None:
        record = self.session.get(EmailAnalysisRecord, analysis_id)
        return EmailAnalysis.model_validate(record.payload) if record else None

    def save_priority_result(self, priority_result: PriorityResult) -> None:
        self.session.merge(
            PriorityResultRecord(
                id=priority_result.id,
                email_id=priority_result.email_id,
                score=priority_result.score,
                band=priority_result.band.value,
                calculated_at=priority_result.calculated_at,
                ruleset_version=priority_result.ruleset_version,
                payload=priority_result.model_dump(mode="json"),
            )
        )

    def save_context(self, context: RetrievedContext) -> None:
        self.session.merge(
            RetrievedContextRecord(
                id=context.id,
                query_email_id=context.query_email_id,
                source_email_ids=context.source_email_ids,
                retrieval_method=context.retrieval_method.value,
                relevance_score=context.relevance_score,
                payload=context.model_dump(mode="json"),
            )
        )

    def save_preference(self, preference: UserPreference) -> None:
        self.session.merge(
            UserPreferenceRecord(
                id=preference.id,
                preference_type=preference.preference_type.value,
                effect=preference.effect.value,
                weight=preference.weight,
                enabled=preference.enabled,
                payload=preference.model_dump(mode="json"),
            )
        )

    def list_preferences(self) -> list[UserPreference]:
        return [
            UserPreference.model_validate(record.payload)
            for record in self.session.query(UserPreferenceRecord).all()
        ]

    def save_action(self, action: ProposedAction) -> None:
        self.session.merge(
            ProposedActionRecord(
                id=action.id,
                email_id=action.email_id,
                description=action.description,
                action_type=action.action_type.value,
                source=action.source.value,
                payload=action.model_dump(mode="json"),
            )
        )

    def save_proposal(self, proposal: CalendarEventProposal) -> None:
        self.session.merge(
            CalendarEventProposalRecord(
                id=proposal.id,
                email_id=proposal.email_id,
                title=proposal.title,
                start_at=proposal.start_at,
                status=proposal.status.value,
                source=proposal.source.value,
                provider_event_id=proposal.provider_event_id,
                payload=proposal.model_dump(mode="json"),
            )
        )

    def get_proposal(self, proposal_id: str) -> CalendarEventProposal | None:
        record = self.session.get(CalendarEventProposalRecord, proposal_id)
        return CalendarEventProposal.model_validate(record.payload) if record else None

    def save_approval(self, approval: ToolApproval) -> None:
        self.session.merge(
            ToolApprovalRecord(
                id=approval.id,
                proposal_id=approval.proposal_id,
                tool_name=approval.tool_name,
                decision=approval.decision.value,
                decided_at=approval.decided_at,
                execution_status=approval.execution_status,
                external_result_id=approval.external_result_id,
                payload=approval.model_dump(mode="json"),
            )
        )
