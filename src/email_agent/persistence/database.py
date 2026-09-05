from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from email_agent.config import Settings


def make_engine(settings: Settings) -> Engine:
    return create_engine(settings.database_url)


def make_session_factory(settings: Settings) -> sessionmaker[Session]:
    return sessionmaker(make_engine(settings), expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session]:
    with session_factory() as session:
        with session.begin():
            yield session
