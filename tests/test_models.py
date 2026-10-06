import pytest
from pydantic import ValidationError

from app.models import ResearchRequest


def test_valid_research_request():
    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    assert request.company == "OpenAI"
    assert request.question == "What are its major products?"


def test_empty_company_is_rejected():
    with pytest.raises(ValidationError):
        ResearchRequest(
            company="",
            question="What are its major products?",
        )


def test_empty_question_is_rejected():
    with pytest.raises(ValidationError):
        ResearchRequest(
            company="OpenAI",
            question="",
        )

from app.models import (
    AnalysisInput,
    AnalysisResult,
    ResearchRequest,
    RetrievedData,
    Source,
    WritingInput,
)


def test_analysis_input_contains_request_and_retrieved_data():
    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    retrieved = RetrievedData(
        sources=[
            Source(
                title="Example",
                url="https://example.com",
                content="Example content",
            )
        ]
    )

    data = AnalysisInput(
        request=request,
        retrieved_data=retrieved,
    )

    assert data.request.company == "OpenAI"
    assert len(data.retrieved_data.sources) == 1


def test_writing_input_contains_analysis_and_sources():
    request = ResearchRequest(
        company="OpenAI",
        question="What are its major products?",
    )

    analysis = AnalysisResult(
        findings=[
            {
                "topic": "Products",
                "fact": "Example product",
                "source_urls": ["https://example.com"],
            }
        ]
    )

    source = Source(
        title="Example",
        url="https://example.com",
        content="Example content",
    )

    data = WritingInput(
        request=request,
        analysis=analysis,
        sources=[source],
    )

    assert data.request.company == "OpenAI"
    assert len(data.analysis.findings) == 1
    assert data.sources[0].url == "https://example.com"