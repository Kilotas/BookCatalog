from pydantic import BaseModel, Field, validator
from typing import Optional, List
from library_catalog.core.constants import (
    MAX_TITLE_LENGTH,
    DEFAULT_TITLE,
    MIN_PUBLISH_YEAR,
    MAX_PUBLISH_YEAR,
    MIN_RATING,
    MAX_RATING,
    MIN_COVER_ID,
)


class OpenLibrarySearchDoc(BaseModel):
    """Документ из поиска Open Library."""

    title: str
    author_name: Optional[List[str]] = Field(None, alias="author_name")
    cover_i: Optional[int] = Field(None, alias="cover_i", ge=MIN_COVER_ID)
    subject: Optional[List[str]] = None
    publisher: Optional[List[str]] = None
    language: Optional[List[str]] = None
    ratings_average: Optional[float] = Field(
        None, alias="ratings_average", ge=MIN_RATING, le=MAX_RATING
    )

    class Config:
        populate_by_name = True

    @validator("title", pre=True)
    def validate_title(cls, value):
        """Валидация заголовка."""
        if not value:
            return DEFAULT_TITLE

        if isinstance(value, str) and len(value) > MAX_TITLE_LENGTH:
            return value[:MAX_TITLE_LENGTH] + "..."

        return value

    @validator("cover_i", pre=True)
    def validate_cover_id(cls, value):
        """Валидация ID обложки."""
        if value is None:
            return None

        if isinstance(value, str) and value.isdigit():
            value = int(value)

        if isinstance(value, (int, float)) and value >= MIN_COVER_ID:
            return int(value)

        return None

    @validator("ratings_average", pre=True)
    def validate_rating(cls, value):
        """Валидация рейтинга."""
        if value is None:
            return None

        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return None

        if isinstance(value, (int, float)):
            value = float(value)
            if value < MIN_RATING:
                return MIN_RATING
            if value > MAX_RATING:
                return MAX_RATING
            return value

        return None

    @validator("author_name", "subject", "publisher", "language", pre=True)
    def convert_to_list(cls, value):
        """Конвертируем строки в списки."""
        if value is None:
            return None

        if isinstance(value, str):
            return [value]

        if isinstance(value, list):
            return value

        return [str(value)]


class OpenLibrarySearchResponse(BaseModel):
    """Ответ от /search.json"""

    numFound: int = Field(..., ge=0)
    docs: List[OpenLibrarySearchDoc]
