from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm import Session

from utils.databases import session_factory as sa_session_factory


class UnitOfWork:
    def __init__(self, session_factory: Callable[[], Session] | None = None) -> None:
        session_factory = session_factory or sa_session_factory
        self._session = session_factory()

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        self.close()

    @property
    def session(self) -> Session:
        return self._session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        self._session.close()