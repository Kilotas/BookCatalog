import logging
from uuid import UUID

from ...domain.exceptions import BookNotFoundException
from ..uow.protocol import UnitOfWorkProtocol

logger = logging.getLogger(__name__)


class DeleteBookCommand:
    """
    Команда удаления книги.
    """

    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def execute(self, book_id: UUID) -> None:
        """
        Удалить книгу.

        Raises:
            BookNotFoundException
        """
        logger.debug("DeleteBookCommand: book_id=%s", book_id)
        deleted = await self.uow.books.delete(book_id)
        if not deleted:
            raise BookNotFoundException(book_id)

        await self.uow.commit()
