from ...data.models.book import Book
from ...api.v1.schemas.book import ShowBook


class BookMapper:
    """Маппер для преобразования Book entity в DTO."""

    @staticmethod
    def to_show_book(book: Book) -> ShowBook:
        """
        Преобразовать ORM модель Book в DTO ShowBook.

        Args:
            book (Book): ORM объект SQLAlchemy.

        Returns:
            ShowBook: Pydantic DTO для отдачи наружу.
        """
        if book is None:
            return None

        return ShowBook(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            year=book.year,
            genre=book.genre,
            pages=book.pages,
            available=book.available,
            isbn=book.isbn,
            description=book.description,
            extra=book.extra,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

    @staticmethod
    def to_show_books(books: list[Book]) -> list[ShowBook]:
        """Преобразовать список ORM-книг в список DTO."""
        return [BookMapper.to_show_book(book) for book in books]
