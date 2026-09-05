from email_agent.persistence.models import Base


def test_core_persistence_tables_are_mapped() -> None:
    assert {
        "emails",
        "email_threads",
        "processed_emails",
        "retrieved_contexts",
        "analysis_signals",
        "email_analyses",
        "priority_results",
        "user_preferences",
        "proposed_actions",
        "calendar_event_proposals",
        "tool_approvals",
    } <= set(Base.metadata.tables)
