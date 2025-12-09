import httpx
from typing import Dict, Any, Optional


from library_catalog.external.base.base_client import BaseApiClient


class OpenLibraryClient(BaseApiClient):
    """Клиент для Open Library API."""

    def __init__(
        self,
        base_url: str = "https://openlibrary.org",
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
    ):
        super().__init__(base_url, timeout, retries, backoff)

    def client_name(self) -> str:
        return "openlibrary"

    async def search_by_isbn(self, isbn: str) -> Dict[str, Any]:
        """
        Поиск книги по ISBN.

        Args:
            isbn: ISBN-10 или ISBN-13

        Returns:
            dict: Данные книги или пустой словарь
        """
        try:
            data = await self._get("/search.json", params={"isbn": isbn, "limit": 1})

            docs = data.get("docs", [])
            if not docs:
                return {}

            return self._extract_book_data(docs[0])

        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout searching by ISBN {isbn}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error searching by ISBN {isbn}: {e}")
            return {}

    async def search_by_title_author(self, title: str, author: str) -> Dict[str, Any]:
        """Поиск по названию и автору."""
        try:
            data = await self._get(
                "/search.json", params={"title": title, "author": author, "limit": 1}
            )

            docs = data.get("docs", [])
            if not docs:
                return {}

            return self._extract_book_data(docs[0])

        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout searching by title/author: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error searching by title/author: {e}")
            return {}

    async def enrich(
        self,
        title: str,
        author: str,
        isbn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Обогатить данные книги.

        Сначала пытается найти по ISBN, затем по title+author.

        Returns:
            dict: Обогащенные данные или пустой словарь
        """
        if isbn:
            data = await self.search_by_isbn(isbn)
            if data:
                return data

        return await self.search_by_title_author(title, author)

    def _extract_book_data(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлечь нужные поля из ответа Open Library.

        Args:
            doc: Документ из массива docs

        Returns:
            dict: Обработанные данные
        """
        result = {}

        if title := doc.get("title"):
            result["title"] = title

        if authors := doc.get("author_name"):
            if isinstance(authors, list) and authors:
                result["author"] = authors[0]
            elif authors:
                result["author"] = authors

        if cover_id := doc.get("cover_i"):
            result["cover_url"] = (
                f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            )

        if subjects := doc.get("subject"):
            if isinstance(subjects, list):
                result["subjects"] = subjects[:10]  # Первые 10
            else:
                result["subjects"] = [subjects]

        if publisher := doc.get("publisher"):
            if isinstance(publisher, list) and publisher:
                result["publisher"] = publisher[0]
            else:
                result["publisher"] = publisher

        if publish_year := doc.get("first_publish_year"):
            result["publish_year"] = publish_year

        if language := doc.get("language"):
            if isinstance(language, list) and language:
                result["language"] = language[0]
            else:
                result["language"] = language

        if isbns := doc.get("isbn"):
            if isinstance(isbns, list) and isbns:
                result["isbn"] = isbns[0]
            else:
                result["isbn"] = isbns

        if ratings := doc.get("ratings_average"):
            result["rating"] = ratings

        return result

    def _get_cover_url(self, cover_id: int | None) -> str | None:
        """Получить URL обложки."""
        if not cover_id:
            return None
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
