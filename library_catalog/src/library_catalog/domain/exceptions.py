from datetime import datetime
from ..core.exceptions import AppException, NotFoundException
from uuid import UUID


class BookNotFoundException(NotFoundException):
    """Книга не найдена."""

    def __init__(self, book_id: UUID):
        super().__init__(resource="Book", identifier=book_id)
        self.book_id = book_id


class BookAlreadyExistsException(AppException):
    """Книга с таким ISBN уже существует."""

    def __init__(self, isbn: str):
        super().__init__(
            message=f"Book with ISBN '{isbn}' already exists",
            status_code=409,
        )
        self.isbn = isbn


class InvalidYearException(AppException):
    """Невалидный год издания."""

    def __init__(self, year: int):
        current_year = datetime.now().year
        super().__init__(
            message=f"Year {year} is invalid (must be between 1000 and {current_year})",
            status_code=400,
        )
        self.year = year
        self.current_year = current_year


class InvalidPagesException(AppException):
    """Невалидное количество страниц."""

    def __init__(self, pages: int):
        super().__init__(
            message=f"Pages count must be positive, got {pages}",
            status_code=400,
        )
        self.pages = pages


class OpenLibraryException(AppException):
    """Ошибка Open Library API."""

    def __init__(self, message: str):
        super().__init__(
            message=f"Open Library API error: {message}",
            status_code=503,
        )
        self.original_message = message


class OpenLibraryTimeoutException(AppException):
    """Таймаут при обращении к Open Library API."""

    def __init__(self, timeout: float):
        super().__init__(
            message=f"Open Library API timeout after {timeout}s",
            status_code=504,
        )
        self.timeout = timeout
