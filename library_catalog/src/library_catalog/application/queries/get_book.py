import logging
from uuid import UUID

from ...api.v1.schemas.book import ShowBook
from ...domain.exceptions import BookNotFoundException
from ...domain.mappers.book_mapper import BookMapper
from ..uow.protocol import UnitOfWorkProtocol

logger = logging.getLogger(__name__)


class GetBookQuery:
    """
    Запрос получения книги по ID.
    """

    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def execute(self, book_id: UUID) -> ShowBook:
        """
        Получить книгу по ID.

        Raises:
            BookNotFoundException
        """
        logger.debug("GetBookQuery: book_id=%s", book_id)
        book = await self.uow.books.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(book_id)
        return BookMapper.to_show_book(book)
