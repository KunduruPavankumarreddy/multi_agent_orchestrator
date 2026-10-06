from typing import Protocol

from app.models import Source


class SearchProvider(Protocol):
    async def search(self, query: str) -> list[Source]:
        """Search for sources matching a query."""
        ...