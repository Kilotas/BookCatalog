import logging
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models.book import Book
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)
        self.session = session

    def _apply_filters(
        self,
        stmt: Select,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
    ) -> Select:
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
        return stmt

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
        logger.debug(
            "BookRepository.find_by_filters: title=%s author=%s genre=%s year=%s available=%s limit=%s offset=%s",
            title, author, genre, year, available, limit, offset,
        )
        try:
            stmt = select(Book)
            stmt = self._apply_filters(stmt, title=title, author=author, genre=genre, year=year, available=available)
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            books = list(result.scalars().all())

            logger.debug("BookRepository.find_by_filters: found=%s", len(books))
            return books
        except SQLAlchemyError:
            logger.exception("BookRepository.find_by_filters: DB error")
            raise

    async def count_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> int:
        logger.debug(
            "BookRepository.count_by_filters: title=%s author=%s genre=%s year=%s available=%s",
            title, author, genre, year, available,
        )
        try:
            stmt = select(func.count(Book.book_id))
            stmt = self._apply_filters(stmt, title=title, author=author, genre=genre, year=year, available=available)

            result = await self.session.execute(stmt)
            count = result.scalar_one() or 0

            logger.debug("BookRepository.count_by_filters: count=%s", count)
            return count
        except SQLAlchemyError:
            logger.exception("BookRepository.count_by_filters: DB error")
            raise

    async def find_by_isbn(self, isbn: str) -> Book | None:
        logger.debug("BookRepository.find_by_isbn: isbn=%s", isbn)
        try:
            stmt = select(Book).where(Book.isbn == isbn)
            result = await self.session.execute(stmt)
            book = result.scalar_one_or_none()
            logger.debug("BookRepository.find_by_isbn: found=%s", bool(book))
            return book
        except SQLAlchemyError:
            logger.exception("BookRepository.find_by_isbn: DB error")
            raise
