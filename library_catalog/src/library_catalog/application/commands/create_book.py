import logging

from ...api.v1.schemas.book import BookCreate, ShowBook
from ...domain.exceptions import BookAlreadyExistsException, OpenLibraryException
from ...domain.mappers.book_mapper import BookMapper
from ...domain.validators.book_validator import BookValidator
from ..uow.protocol import UnitOfWorkProtocol
from ...external.protocols import MetadataGatewayProtocol

logger = logging.getLogger(__name__)


class CreateBookCommand:
    """
    Команда создания книги.

    Выполняет валидацию, бизнес-правила, обогащение и фиксирует транзакцию.
    """

    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        metadata_gateway: MetadataGatewayProtocol,
        validator: BookValidator,
    ):
        self.uow = uow
        self.metadata_gateway = metadata_gateway
        self.validator = validator

    async def execute(self, data: BookCreate) -> ShowBook:
        """
        Создать книгу.

        Raises:
            BookAlreadyExistsException
        """
        logger.debug("CreateBookCommand: validating data=%s", data.model_dump())
        self.validator.validate_create(data)

        if data.isbn:
            logger.debug("CreateBookCommand: checking isbn=%s", data.isbn)
            existing = await self.uow.books.find_by_isbn(data.isbn)
            if existing:
                logger.info("CreateBookCommand: isbn already exists=%s", data.isbn)
                raise BookAlreadyExistsException(data.isbn)

        extra = await self._enrich(data)

        book = await self.uow.books.create(
            title=data.title,
            author=data.author,
            year=data.year,
            genre=data.genre,
            pages=data.pages,
            isbn=data.isbn,
            description=data.description,
            extra=extra,
        )

        await self.uow.commit()

        return BookMapper.to_show_book(book)

    async def _enrich(self, data: BookCreate) -> dict | None:
        """
        Обогатить книгу из внешнего источника метаданных.

        Не выбрасывает исключение при недоступности внешнего API.
        """
        try:
            extra = await self.metadata_gateway.enrich(
                title=data.title,
                author=data.author,
                isbn=data.isbn,
            )
            return extra if extra else None
        except OpenLibraryException:
            logger.warning(
                "CreateBookCommand: metadata enrichment failed",
                extra={"title": data.title, "author": data.author, "isbn": data.isbn},
            )
            return None
