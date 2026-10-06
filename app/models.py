from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    company: str = Field(min_length=1)
    question: str = Field(min_length=1)


class Source(BaseModel):
    title: str
    url: str
    content: str


class RetrievedData(BaseModel):
    sources: list[Source]


class Finding(BaseModel):
    topic: str
    fact: str
    source_urls: list[str]


class AnalysisResult(BaseModel):
    findings: list[Finding]


class WriterResult(BaseModel):
    answer: str 