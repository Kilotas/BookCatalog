from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db, async_session_maker
from ..core.clients import clients_manager

from ..application.uow.protocol import UnitOfWorkProtocol
from ..application.uow.sqlalchemy import SqlAlchemyUnitOfWork

from ..external.protocols import MetadataGatewayProtocol
from ..domain.services.book_service import BookService


def get_metadata_gateway() -> MetadataGatewayProtocol:
    """
    Получить источник метаданных о книгах.

    Реализация сейчас: OpenLibraryClient (через ClientsManager).
    """
    return clients_manager.get_openlibrary()


async def get_uow() -> AsyncGenerator[UnitOfWorkProtocol, None]:
    """
    DI для Unit of Work.

    На каждый HTTP-запрос создаётся новый UoW:
    - открывает AsyncSession
    - предоставляет репозитории через одну сессию
    - rollback при исключении
    - закрывает сессию
    """
    uow = SqlAlchemyUnitOfWork(async_session_maker)
    async with uow:
        yield uow


async def get_book_service(
    uow: Annotated[UnitOfWorkProtocol, Depends(get_uow)],
    metadata_gateway: Annotated[MetadataGatewayProtocol, Depends(get_metadata_gateway)],
) -> BookService:
    """
    Создаёт BookService, внедряя:
    - UnitOfWork (транзакции + репозитории)
    - источник метаданных (внешний API)
    """
    return BookService(
        uow=uow,
        metadata_gateway=metadata_gateway,
    )


BookServiceDep = Annotated[BookService, Depends(get_book_service)]
UnitOfWorkDep = Annotated[UnitOfWorkProtocol, Depends(get_uow)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
