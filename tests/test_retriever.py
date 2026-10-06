import asyncio

import pytest

from app.agents.errors import AgentExecutionError
from app.agents.retriever import RetrieverAgent
from app.models import ResearchRequest, Source

from tests.fakes import FakeSearchProvider


@pytest.mark.asyncio
async def test_retriever_collects_results_from_all_queries():
    provider = FakeSearchProvider()
    agent = RetrieverAgent(provider)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    result = await agent.run(request)

    assert len(provider.queries) == 4
    assert len(result.sources) == 4


@pytest.mark.asyncio
async def test_retriever_degrades_when_one_search_fails():
    provider = FakeSearchProvider()
    agent = RetrieverAgent(provider)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    queries = agent.build_queries(request)

    provider.failures.add(queries[1])

    result = await agent.run(request)

    assert len(result.sources) == 3


@pytest.mark.asyncio
async def test_retriever_fails_when_all_searches_fail():
    provider = FakeSearchProvider()
    agent = RetrieverAgent(provider)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    queries = agent.build_queries(request)
    provider.failures.update(queries)

    with pytest.raises(AgentExecutionError) as exc_info:
        await agent.run(request)

    assert exc_info.value.agent_name == "retriever"
    assert exc_info.value.retryable is True


class ConcurrencyTrackingProvider:
    def __init__(self, expected_calls: int) -> None:
        self.expected_calls = expected_calls
        self.started_calls = 0
        self.all_started = asyncio.Event()
        self.release = asyncio.Event()

    async def search(self, query: str) -> list[Source]:
        self.started_calls += 1

        if self.started_calls == self.expected_calls:
            self.all_started.set()

        await self.all_started.wait()
        await self.release.wait()

        return [
            Source(
                title=query,
                url="https://example.com",
                content="test",
            )
        ]


@pytest.mark.asyncio
async def test_retriever_runs_searches_concurrently():
    provider = ConcurrencyTrackingProvider(expected_calls=4)
    agent = RetrieverAgent(provider)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    task = asyncio.create_task(agent.run(request))

    await asyncio.wait_for(provider.all_started.wait(), timeout=1)

    assert provider.started_calls == 4

    provider.release.set()

    result = await task

    assert len(result.sources) == 4