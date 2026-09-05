from email_agent.persistence.database import make_engine, make_session_factory
from email_agent.persistence.repositories import (
    ActionRepository,
    AnalysisRepository,
    ApprovalRepository,
    ContextRepository,
    EmailRepository,
    PreferenceRepository,
    ProposalRepository,
)
from email_agent.persistence.sqlalchemy import SqlAlchemyRepository

__all__ = [
    "ActionRepository",
    "AnalysisRepository",
    "ApprovalRepository",
    "ContextRepository",
    "EmailRepository",
    "PreferenceRepository",
    "ProposalRepository",
    "SqlAlchemyRepository",
    "make_engine",
    "make_session_factory",
]
