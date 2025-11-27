from typing import Any

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    scoped_session,
    sessionmaker,
)

from settings import database_settings, general_settings

NAMING_CONVENTION = {
    "ix": "ix__%(column_0_label)s",
    "uq": "uq__%(table_name)s__%(column_0_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


def make_engine(database_url: URL = database_settings.full_url) -> Engine:
    return create_engine(
        database_url,
        isolation_level="SERIALIZABLE",
        echo=general_settings.debug,
    )


def make_session_factory(
    database_url: URL = database_settings.full_url,
    engine: Engine | None = None,
    autocommit: bool = False,
    autoflush: bool = False,
    expire_on_commit: bool = True,
) -> sessionmaker[Session]:
    """фабрика сессий"""
    engine = engine or make_engine(database_url)

    return sessionmaker(
        bind=engine,
        autocommit=autocommit,
        autoflush=autoflush,
        expire_on_commit=expire_on_commit,
    )


def make_scoped_session_factory(
    database_url: URL | None = None,
) -> scoped_session[Any]:
    """хранилище уже созданных сессий треда"""
    database_url = database_url or database_settings.full_url
    return scoped_session(make_session_factory(database_url))


session_factory = make_session_factory()
scoped_session_factory = make_scoped_session_factory()


class Base(DeclarativeBase):
    """
    Базовый класс для декларативного описания ORM-моделей таблиц БД
    """