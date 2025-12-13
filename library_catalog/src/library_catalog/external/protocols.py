from typing import Protocol

class MetadataGatewayProtocol(Protocol):
    """Интерфейс внешних источников метаданных."""

    async def enrich(
        self,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> dict | None: ...

    async def close(self) -> None: ...