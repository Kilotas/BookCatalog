import logging

from ...api.v1.schemas.book import ShowBook
from ...domain.mappers.book_mapper import BookMapper
from ..uow.protocol import UnitOfWorkProtocol

logger = logging.getLogger(__name__)


class SearchBooksQuery:
    """
    Запрос поиска книг с фильтрацией и пагинацией.
    """

    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def execute(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ShowBook], int]:
        """
        Найти книги по фильтрам и вернуть (items, total).
        """
        logger.debug(
            "SearchBooksQuery: title=%s author=%s genre=%s year=%s available=%s limit=%s offset=%s",
            title,
            author,
            genre,
            year,
            available,
            limit,
            offset,
        )

        books = await self.uow.books.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )

        total = await self.uow.books.count_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )

        return BookMapper.to_show_books(books), total
