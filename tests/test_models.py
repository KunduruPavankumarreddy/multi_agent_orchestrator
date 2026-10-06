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