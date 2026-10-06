import pytest

from app.agents.analyzer import AnalyzerAgent
from app.agents.errors import AgentExecutionError
from app.models import (
    AnalysisInput,
    RetrievedData,
    ResearchRequest,
    Source,
)

from tests.fakes import FakeLLMProvider


@pytest.mark.asyncio
async def test_analyzer_returns_structured_findings():
    llm = FakeLLMProvider(
        response="""
        {
          "findings": [
            {
              "topic": "Products",
              "claim": "OpenAI offers AI products.",
              "evidence": "The source describes AI products.",
              "source_urls": ["https://example.com/openai"]
            }
          ]
        }
        """
    )

    agent = AnalyzerAgent(llm)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    retrieved = RetrievedData(
        sources=[
            Source(
                title="OpenAI Products",
                url="https://example.com/openai",
                content="The company offers several AI products.",
            )
        ]
    )

    result = await agent.run(
        AnalysisInput(
            request=request,
            retrieved_data=retrieved,
        )
    )

    assert len(result.findings) == 1
    assert result.findings[0].topic == "Products"
    assert result.findings[0].claim == "OpenAI offers AI products."
    assert result.findings[0].evidence == "The source describes AI products."
    assert result.findings[0].source_urls == [
        "https://example.com/openai"
    ]


@pytest.mark.asyncio
async def test_analyzer_rejects_unknown_source_url():
    llm = FakeLLMProvider(
        response="""
        {
          "findings": [
            {
              "topic": "Products",
              "claim": "Unsupported claim.",
              "evidence": "Some evidence.",
              "source_urls": ["https://invented.example.com"]
            }
          ]
        }
        """
    )

    agent = AnalyzerAgent(llm)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    retrieved = RetrievedData(
        sources=[
            Source(
                title="Real source",
                url="https://real.example.com",
                content="Real evidence.",
            )
        ]
    )

    with pytest.raises(AgentExecutionError) as exc_info:
        await agent.run(
            AnalysisInput(
                request=request,
                retrieved_data=retrieved,
            )
        )

    assert exc_info.value.agent_name == "analyzer"
    assert exc_info.value.retryable is False
    assert "invented.example.com" in str(exc_info.value)


@pytest.mark.asyncio
async def test_analyzer_rejects_malformed_llm_output():
    llm = FakeLLMProvider(
        response="this is not valid JSON"
    )

    agent = AnalyzerAgent(llm)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    retrieved = RetrievedData(
        sources=[
            Source(
                title="Example",
                url="https://example.com",
                content="Some evidence.",
            )
        ]
    )

    with pytest.raises(AgentExecutionError) as exc_info:
        await agent.run(
            AnalysisInput(
                request=request,
                retrieved_data=retrieved,
            )
        )

    assert exc_info.value.agent_name == "analyzer"
    assert exc_info.value.retryable is True
    assert "Analyzer failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_analyzer_prompt_contains_request_and_source_content():
    llm = FakeLLMProvider(
        response="""
        {
          "findings": []
        }
        """
    )

    agent = AnalyzerAgent(llm)

    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    retrieved = RetrievedData(
        sources=[
            Source(
                title="OpenAI Products",
                url="https://example.com/openai",
                content="OpenAI develops AI products and services.",
            )
        ]
    )

    await agent.run(
        AnalysisInput(
            request=request,
            retrieved_data=retrieved,
        )
    )

    assert len(llm.prompts) == 1

    prompt = llm.prompts[0]

    assert "OpenAI" in prompt
    assert "What are its major products?" in prompt
    assert "https://example.com/openai" in prompt
    assert "OpenAI develops AI products and services." in prompt
    assert "Do not invent facts" in prompt
    assert "untrusted evidence" in prompt