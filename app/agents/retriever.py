import asyncio

from app.agents.base import BaseAgent
from app.agents.errors import AgentExecutionError
from app.models import ResearchRequest, RetrievedData, Source
from app.services.search import SearchProvider


class RetrieverAgent(BaseAgent[ResearchRequest, RetrievedData]):
    name = "retriever"

    def __init__(self, search_provider: SearchProvider) -> None:
        self.search_provider = search_provider

    def build_queries(self, request: ResearchRequest) -> list[str]:
        """Build independent evidence-gathering queries."""
        company = request.company

        return [
            f"{company} {request.question}",
            f"{company} products and services",
            f"{company} latest developments",
            f"{company} competitors and business risks",
        ]

    async def run(self, input_data: ResearchRequest) -> RetrievedData:
        queries = self.build_queries(input_data)

        results = await asyncio.gather(
            *(self.search_provider.search(query) for query in queries),
            return_exceptions=True,
        )

        sources: list[Source] = []
        failures: list[str] = []

        for query, result in zip(queries, results, strict=True):
            if isinstance(result, Exception):
                failures.append(query)
                continue

            sources.extend(result)

        if not sources:
            raise AgentExecutionError(
                agent_name=self.name,
                message="All retrieval operations failed.",
                retryable=True,
            )

        return RetrievedData(sources=sources)