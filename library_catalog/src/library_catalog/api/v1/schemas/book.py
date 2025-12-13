from uuid import UUID
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

from ....core.constants import (
    TITLE_MAX_LENGTH,
    AUTHOR_MAX_LENGTH,
    GENRE_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    ISBN_MAX_LENGTH,
    YEAR_MIN,
    PAGES_MIN,
)



class BookBase(BaseModel):
    title: str = Field(..., max_length=TITLE_MAX_LENGTH)
    author: str = Field(..., max_length=AUTHOR_MAX_LENGTH)
    year: int = Field(..., ge=YEAR_MIN)
    genre: Optional[str] = Field(None, max_length=GENRE_MAX_LENGTH)
    pages: Optional[int] = Field(None, ge=PAGES_MIN)
    isbn: Optional[str] = Field(None, max_length=ISBN_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    extra: Optional[Any] = None



class BookCreate(BookBase):
    available: bool = True

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str | None) -> str | None:
        if v is None:
            return v
        clean = v.replace("-", "").replace(" ", "")
        if not clean.replace("X", "").isdigit():
            raise ValueError("ISBN must contain only digits")
        if len(clean) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 characters")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Clean Code",
                    "author": "Robert C. Martin",
                    "year": 2008,
                    "genre": "Programming",
                    "pages": 464,
                    "isbn": "978-0132350884",
                    "description": "A Handbook of Agile Software Craftsmanship",
                    "available": True,
                }
            ]
        }
    }


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=TITLE_MAX_LENGTH)
    author: Optional[str] = Field(None, max_length=AUTHOR_MAX_LENGTH)
    year: Optional[int] = Field(None, ge=YEAR_MIN)
    genre: Optional[str] = Field(None, max_length=GENRE_MAX_LENGTH)
    pages: Optional[int] = Field(None, ge=PAGES_MIN)
    isbn: Optional[str] = Field(None, max_length=ISBN_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    extra: Optional[Any] = None
    available: Optional[bool] = None


class ShowBook(BookBase):
    book_id: UUID
    available: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "book_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Clean Code",
                    "author": "Robert C. Martin",
                    "year": 2008,
                    "genre": "Programming",
                    "pages": 464,
                    "available": True,
                    "isbn": "978-0132350884",
                    "description": "A classic book on software craftsmanship",
                    "extra": {
                        "cover_url": "https://covers.openlibrary.org/b/id/123-L.jpg",
                        "subjects": ["Software craftsmanship", "Engineering"],
                    },
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:00:00",
                }
            ]
        },
    )
