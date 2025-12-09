import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.library_catalog.core.database import Base

from .constants import (
    TITLE_MAX_LENGTH,
    AUTHOR_MAX_LENGTH,
    GENRE_MAX_LENGTH,
    ISBN_MAX_LENGTH,
)


class Book(Base):
    """
    ORM-модель книги (Book) для каталога библиотеки.

    Хранит основную информацию о книге:
    - идентификатор UUID
    - название, автор, год, жанр
    - количество страниц
    - статус доступности
    - ISBN, описание, дополнительные данные (JSON)
    """

    __tablename__ = "books"

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(TITLE_MAX_LENGTH),
        nullable=False,
        index=True,
    )

    author: Mapped[str] = mapped_column(
        String(AUTHOR_MAX_LENGTH),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    genre: Mapped[str] = mapped_column(
        String(GENRE_MAX_LENGTH),
        nullable=False,
        index=True,
    )

    pages: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    isbn: Mapped[str | None] = mapped_column(
        String(ISBN_MAX_LENGTH),
        unique=True,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extra: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.book_id}, title='{self.title}')>"
