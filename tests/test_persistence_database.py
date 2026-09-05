from pathlib import Path

from sqlalchemy import text

from email_agent.config import Settings
from email_agent.persistence import make_engine, make_session_factory
from email_agent.persistence.database import session_scope


def build_settings(**values: object) -> Settings:
    return Settings(**{"_env_file": None, **values})


def test_sqlite_connection_uses_settings_database_url(tmp_path: Path) -> None:
    settings = build_settings(database_url=f"sqlite:///{tmp_path / 'email_agent.db'}")
    engine = make_engine(settings)

    with engine.connect() as connection:
        assert connection.execute(text("select 1")).scalar_one() == 1


def test_session_scope_commits_transaction(tmp_path: Path) -> None:
    settings = build_settings(database_url=f"sqlite:///{tmp_path / 'email_agent.db'}")
    session_factory = make_session_factory(settings)

    with session_scope(session_factory) as session:
        assert session.execute(text("select 1")).scalar_one() == 1
