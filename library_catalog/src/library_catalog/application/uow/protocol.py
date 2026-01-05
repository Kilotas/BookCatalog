from typing import Protocol
from uuid import UUID

from ...data.models.book import Book


class BookRepositoryProtocol(Protocol):
    """Интерфейс книжного репозитория."""

    async def create(self, **kwargs) -> Book: ...

    async def get_by_id(self, id: UUID) -> Book | None: ...

    async def find_by_isbn(self, isbn: str) -> Book | None: ...


class UnitOfWorkProtocol(Protocol):
    """Интерфейс Unit of Work."""

    books: BookRepositoryProtocol

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "UnitOfWorkProtocol": ...

    async def __aexit__(self, *args) -> None: ...
