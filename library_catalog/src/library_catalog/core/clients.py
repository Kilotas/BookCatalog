from typing import Optional
from ..external.openlibrary.client import OpenLibraryClient
from ..core.config import settings


class ClientsManager:
    """
    Менеджер для управления lifecycle внешних клиентов.

    Преимущества:
    - Lazy initialization
    - Proper cleanup при shutdown
    - Легко добавить новые клиенты
    - Можно мокировать в тестах
    """

    def __init__(self):
        self._openlibrary: Optional[OpenLibraryClient] = None

    def get_openlibrary(self) -> OpenLibraryClient:
        """
        Получить OpenLibrary клиент (lazy initialization).

        Создается только при первом обращении и переиспользуется.
        """
        if self._openlibrary is None:
            self._openlibrary = OpenLibraryClient(
                base_url=settings.openlibrary_base_url,
                timeout=settings.openlibrary_timeout,
                retries=settings.openlibrary_retries,
                backoff=settings.openlibrary_backoff,
            )
        return self._openlibrary

    async def close_all(self):
        """
        Закрыть все клиенты.

        Вызывается при shutdown приложения.
        """
        if self._openlibrary:
            await self._openlibrary.close()
            self._openlibrary = None

clients_manager = ClientsManager()