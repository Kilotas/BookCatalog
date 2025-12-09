from abc import ABC, abstractmethod
import asyncio
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BaseApiClient(ABC):
    """
    Базовый класс для HTTP клиентов внешних API.

    Включает:
    - Retry логику
    - Обработку ошибок
    - Логирование
    - Timeout management
    """

    def __init__(
            self,
            base_url: str,
            timeout: float = 10.0,
            retries: int = 3,
            backoff: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=self.timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            follow_redirects=True,
        )

        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """
        Имя клиента для логирования.

        Returns:
            str: Имя клиента (например, "openlibrary")
        """
        pass

    def _build_url(self, path: str) -> str:
        """
        Построить полный URL.

        Args:
            path: Путь endpoint

        Returns:
            str: Полный URL
        """
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def _request(
            self,
            method: str,
            path: str,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос с retry логикой.

        Args:
            method: HTTP метод (GET, POST, etc.)
            path: Путь endpoint
            params: Query параметры
            json: JSON тело запроса
            headers: HTTP заголовки

        Returns:
            dict: JSON ответ

        Raises:
            httpx.TimeoutException: При таймауте
            httpx.HTTPError: При HTTP ошибке
        """
        url = self._build_url(path)

        if headers is None:
            headers = {}

        headers.setdefault("User-Agent", f"{self.client_name()}-client/1.0")
        headers.setdefault("Accept", "application/json")

        for attempt in range(self.retries):
            try:
                self.logger.debug(
                    f"[Attempt {attempt + 1}/{self.retries}] {method} {url} "
                    f"params={params}"
                )

                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )


                response.raise_for_status()


                if response.status_code == 204 or not response.content:
                    return {}


                try:
                    return response.json()
                except ValueError as e:
                    self.logger.error(f"Failed to parse JSON: {e}")
                    return {}

            except httpx.TimeoutException:
                self.logger.warning(f"Timeout on attempt {attempt + 1}")

                if attempt == self.retries - 1:
                    self.logger.error(f"Timeout after {self.retries} attempts to {url}")
                    raise httpx.TimeoutException(
                        f"Request timed out after {self.timeout}s"
                    )


                wait_time = self.backoff * (2 ** attempt)
                self.logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                self.logger.warning(f"HTTP error {e.response.status_code}")


                if e.response.status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2 ** attempt)
                    self.logger.info(f"Server error, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(
                        f"HTTP {e.response.status_code} error: {e.response.text[:200]}"
                    )
                    raise

            except httpx.RequestError as e:
                self.logger.error(f"Request error: {e}")

                if attempt == self.retries - 1:
                    self.logger.error(f"Request failed after {self.retries} attempts")
                    raise

                wait_time = self.backoff * (2 ** attempt)
                self.logger.info(f"Network error, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)


        raise httpx.RequestError("Max retries exceeded")

    async def _get(
            self,
            path: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить GET запрос.

        Args:
            path: Путь endpoint
            params: Query параметры
            headers: HTTP заголовки

        Returns:
            dict: JSON ответ
        """
        return await self._request("GET", path, params=params, headers=headers)

    async def _post(
            self,
            path: str,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить POST запрос.

        Args:
            path: Путь endpoint
            json: JSON тело запроса
            headers: HTTP заголовки

        Returns:
            dict: JSON ответ
        """
        return await self._request("POST", path, json=json, headers=headers)

    async def close(self) -> None:
        """
        Закрыть HTTP клиент.

        Освобождает ресурсы и соединения.
        """
        if self._client:
            await self._client.aclose()
            self.logger.debug("HTTP client closed")

    async def __aenter__(self):
        """Поддержка async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие клиента при выходе из контекста."""
        await self.close()