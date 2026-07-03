from pydantic import BaseModel


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    research_id: str
    status: str = "queued"


class ResearchResult(BaseModel):
    research_id: str
    topic: str
    query: str = ""
    sources: list[dict] = []
    verified_claims: list[dict] = []
    report: str = ""
    presentation: str = ""
    error: str | None = None
    done: bool = False
    timestamp: str = ""


class ResearchList(BaseModel):
    researches: list[ResearchResult]
