from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from .protocol import UnitOfWorkProtocol
from ...data.repositories.book_repository import BookRepository


class SqlAlchemyUnitOfWork(UnitOfWorkProtocol):
    """Реализация UnitOfWork через SQLAlchemy."""

    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self.books: BookRepository | None = None

    async def __aenter__(self):
        self._session = self._session_factory()
        self.books = BookRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
