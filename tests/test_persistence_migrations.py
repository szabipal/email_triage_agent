from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_migration_creates_core_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "email_agent.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

    command.upgrade(config, "head")

    inspector = inspect(create_engine(f"sqlite:///{database_path}"))
    assert {
        "emails",
        "processed_emails",
        "analysis_signals",
        "email_analyses",
        "priority_results",
        "calendar_event_proposals",
        "tool_approvals",
    } <= set(inspector.get_table_names())
    assert "uq_emails_provider_message_id" in {
        index["name"] for index in inspector.get_indexes("emails")
    }
