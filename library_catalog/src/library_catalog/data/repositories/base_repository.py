from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Универсальный CRUD репозиторий.

    ВАЖНО: Репозиторий НЕ делает commit - это ответственность вызывающего кода.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        """
        Создать запись БЕЗ commit.

        flush() генерирует ID и проверяет constraints,
        но оставляет commit() вызывающему коду.
        """
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, id: UUID) -> T | None:
        """Получить по первичному ключу."""
        return await self.session.get(self.model, id)

    async def update(self, id: UUID, **kwargs) -> T | None:
        """Обновить запись БЕЗ commit."""
        obj = await self.get_by_id(id)
        if obj is None:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: UUID) -> bool:
        """Удалить запись БЕЗ commit."""
        obj = await self.get_by_id(id)
        if obj is None:
            return False

        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Получить список записей."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())