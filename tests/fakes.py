from app.models import Source


class FakeSearchProvider:
    def __init__(
        self,
        *,
        failures: set[str] | None = None,
    ) -> None:
        self.failures = failures or set()
        self.queries: list[str] = []

    async def search(self, query: str) -> list[Source]:
        self.queries.append(query)

        if query in self.failures:
            raise RuntimeError(f"Search failed for: {query}")

        return [
            Source(
                title=f"Result for {query}",
                url=f"https://example.com/{len(self.queries)}",
                content=f"Evidence retrieved for {query}",
            )
        ]