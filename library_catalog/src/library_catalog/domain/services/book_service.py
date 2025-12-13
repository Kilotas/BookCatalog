import logging
from uuid import UUID

from ...api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from ...application.uow.protocol import UnitOfWorkProtocol
from ...external.protocols import MetadataGatewayProtocol
from ..validators.book_validator import BookValidator
from ...application.commands.create_book import CreateBookCommand
from ...application.commands.update_book import UpdateBookCommand
from ...application.commands.delete_book import DeleteBookCommand
from ...application.queries.get_book import GetBookQuery
from ...application.queries.search_books import SearchBooksQuery

logger = logging.getLogger(__name__)


class BookService:
    """
    Фасад над CQRS-командами и запросами.

    """

    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        metadata_gateway: MetadataGatewayProtocol,
    ) -> None:
        self._uow = uow
        self._metadata_gateway = metadata_gateway

        validator = BookValidator()

        self._create_cmd = CreateBookCommand(
            uow=self._uow,
            metadata_gateway=self._metadata_gateway,
            validator=validator,
        )
        self._update_cmd = UpdateBookCommand(
            uow=self._uow,
            validator=validator,
        )
        self._delete_cmd = DeleteBookCommand(
            uow=self._uow,
        )

        self._get_query = GetBookQuery(
            uow=self._uow,
        )
        self._search_query = SearchBooksQuery(
            uow=self._uow,
        )


    async def create_book(self, data: BookCreate) -> ShowBook:
        logger.debug("BookService.create_book: data=%s", data.model_dump())
        result = await self._create_cmd.execute(data)
        logger.info(
            "BookService.create_book: created book title=%s author=%s",
            result.title,
            result.author,
        )
        return result

    async def update_book(self, book_id: UUID, data: BookUpdate) -> ShowBook:
        logger.debug(
            "BookService.update_book: id=%s data=%s",
            book_id,
            data.model_dump(),
        )
        result = await self._update_cmd.execute(book_id, data)
        logger.info("BookService.update_book: updated book id=%s", book_id)
        return result

    async def delete_book(self, book_id: UUID) -> None:
        logger.debug("BookService.delete_book: id=%s", book_id)
        await self._delete_cmd.execute(book_id)
        logger.info("BookService.delete_book: deleted book id=%s", book_id)


    async def get_book(self, book_id: UUID) -> ShowBook:
        logger.debug("BookService.get_book: id=%s", book_id)
        result = await self._get_query.execute(book_id)
        logger.info("BookService.get_book: found book id=%s", book_id)
        return result

    async def search_books(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ShowBook], int]:
        logger.debug(
            "BookService.search_books: filters title=%s author=%s genre=%s "
            "year=%s available=%s limit=%s offset=%s",
            title,
            author,
            genre,
            year,
            available,
            limit,
            offset,
        )

        books, total = await self._search_query.execute(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )

        logger.info(
            "BookService.search_books: result_count=%s total=%s",
            len(books),
            total,
        )
        return books, total
