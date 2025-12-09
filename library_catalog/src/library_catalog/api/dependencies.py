from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.config import settings

from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService

from ..external.openlibrary.client import OpenLibraryClient




@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    """
    Создать и вернуть singleton OpenLibraryClient.
    LRU cache гарантирует, что клиент создастся один раз.
    """
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
        retries=settings.openlibrary_retries,
        backoff=settings.openlibrary_backoff,
    )




async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    """
    Возвращает экземпляр BookRepository.
    Создаётся новый репозиторий на каждый HTTP запрос.
    """
    return BookRepository(db)




async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    """
    Создаёт BookService, внедряя в него:
    - репозиторий (локальная БД)
    - клиент OpenLibrary (внешние данные)
    """
    return BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )




BookServiceDep = Annotated[BookService, Depends(get_book_service)]
BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
