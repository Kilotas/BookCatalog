from datetime import datetime

from ..exceptions import InvalidYearException, InvalidPagesException
from ...api.v1.schemas.book import BookCreate, BookUpdate


class BookValidator:
    """
    Валидатор бизнес-правил для книги.

    Используется командами/сервисами, чтобы не держать валидацию внутри CRUD.
    """

    def validate_create(self, data: BookCreate) -> None:
        """
        Валидация при создании книги.

        Raises:
            InvalidYearException
            InvalidPagesException
        """
        self._validate_year(data.year)
        self._validate_pages(data.pages)

    def validate_update(self, data: BookUpdate) -> None:
        """
        Валидация при обновлении книги (только переданные поля).

        Raises:
            InvalidYearException
            InvalidPagesException
        """
        if data.year is not None:
            self._validate_year(data.year)
        if data.pages is not None:
            self._validate_pages(data.pages)

    def _validate_year(self, year: int) -> None:
        """
        Проверить корректность года.

        Raises:
            InvalidYearException
        """
        current_year = datetime.now().year
        if year < 1000 or year > current_year:
            raise InvalidYearException(year)

    def _validate_pages(self, pages: int) -> None:
        """
        Проверить корректность количества страниц.

        Raises:
            InvalidPagesException
        """
        if pages <= 0:
            raise InvalidPagesException(pages)
