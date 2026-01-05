import logging
from uuid import UUID

from ...api.v1.schemas.book import BookUpdate, ShowBook
from ...domain.exceptions import BookNotFoundException
from ...domain.mappers.book_mapper import BookMapper
from ...domain.validators.book_validator import BookValidator
from ..uow.protocol import UnitOfWorkProtocol

logger = logging.getLogger(__name__)


class UpdateBookCommand:
    """
    Команда обновления книги.
    """

    def __init__(self, uow: UnitOfWorkProtocol, validator: BookValidator):
        self.uow = uow
        self.validator = validator

    async def execute(self, book_id: UUID, data: BookUpdate) -> ShowBook:
        """
        Обновить книгу.

        Raises:
            BookNotFoundException
        """
        logger.debug("UpdateBookCommand: book_id=%s data=%s", book_id, data.model_dump())
        existing = await self.uow.books.get_by_id(book_id)
        if existing is None:
            raise BookNotFoundException(book_id)

        self.validator.validate_update(data)

        updated = await self.uow.books.update(
            book_id,
            **data.model_dump(exclude_unset=True),
        )

        await self.uow.commit()

        return BookMapper.to_show_book(updated)
