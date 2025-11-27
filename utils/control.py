from collections.abc import Callable, Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def session_control(session_factory: Callable[..., Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()