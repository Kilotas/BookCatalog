from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """
    Репозиторий для работы с книгами.
    Содержит CRUD из BaseRepository и дополнительные методы фильтрации.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    # --------------------------------------------------------------------------
    async def find_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> list[Book]:
        stmt = select(Book)

        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))
        if genre:
            stmt = stmt.where(Book.genre == genre)
        if year is not None:
            stmt = stmt.where(Book.year == year)
        if available is not None:
            stmt = stmt.where(Book.available == available)

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Получить книгу по точному ISBN."""

        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --------------------------------------------------------------------------
    async def count_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> int:
        """Подсчитать количество книг, подходящих под фильтры."""

        stmt = select(func.count(Book.book_id))
        conditions = []

        if title is not None:
            conditions.append(Book.title.ilike(f"%{title}%"))

        if author is not None:
            conditions.append(Book.author.ilike(f"%{author}%"))

        if genre is not None:
            conditions.append(Book.genre.ilike(f"%{genre}%"))

        if year is not None:
            conditions.append(Book.year == year)

        if available is not None:
            conditions.append(Book.available == available)

        if conditions:
            stmt = stmt.where(*conditions)

        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count or 0
