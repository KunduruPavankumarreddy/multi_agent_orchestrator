from fastapi import FastAPI

from app.models import ResearchRequest

app = FastAPI(title="Multi-Agent Research Orchestrator")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/research")
async def research(request: ResearchRequest) -> dict:
    return {
        "message": "Research request accepted",
        "company": request.company,
        "question": request.question,
    }