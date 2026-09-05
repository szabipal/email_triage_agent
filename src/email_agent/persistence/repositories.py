from __future__ import annotations

from typing import Protocol

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


class EmailRepository(Protocol):
    def save_email(self, email: Email) -> None: ...

    def get_email(self, email_id: str) -> Email | None: ...

    def list_emails(self) -> list[Email]: ...


class AnalysisRepository(Protocol):
    def save_processed_email(self, processed_email: ProcessedEmail) -> None: ...

    def save_signals(self, signals: EmailAnalysisSignals) -> None: ...

    def save_analysis(self, analysis: EmailAnalysis) -> None: ...

    def save_priority_result(self, priority_result: PriorityResult) -> None: ...


class ContextRepository(Protocol):
    def save_context(self, context: RetrievedContext) -> None: ...


class PreferenceRepository(Protocol):
    def save_preference(self, preference: UserPreference) -> None: ...

    def list_preferences(self) -> list[UserPreference]: ...


class ActionRepository(Protocol):
    def save_action(self, action: ProposedAction) -> None: ...


class ProposalRepository(Protocol):
    def save_proposal(self, proposal: CalendarEventProposal) -> None: ...

    def get_proposal(self, proposal_id: str) -> CalendarEventProposal | None: ...


class ApprovalRepository(Protocol):
    def save_approval(self, approval: ToolApproval) -> None: ...
