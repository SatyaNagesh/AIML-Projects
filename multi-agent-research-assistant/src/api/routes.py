import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from src.agent.graph import build_research_graph
from src.agent.state import ResearchState
from src.api.schemas import ResearchList, ResearchRequest, ResearchResult
from src.db.repository import ResearchRepository

router = APIRouter(prefix="/api/v1", tags=["research"])


@router.post("/research", status_code=201)
async def create_research(req: ResearchRequest) -> dict:
    research_id = str(uuid.uuid4())
    repo = ResearchRepository()
    await repo.create(research_id=research_id, topic=req.topic)

    graph = build_research_graph()
    state = ResearchState(topic=req.topic)
    result = await graph.ainvoke(state)

    await repo.update(
        research_id=research_id,
        status="completed" if result.get("done") else "failed",
        query=result.get("query", ""),
        sources=result.get("sources", []),
        claims=result.get("verified_claims", []),
        report=result.get("report", ""),
        presentation=result.get("presentation", ""),
        error=result.get("error"),
    )

    return {
        "research_id": research_id,
        "status": "completed" if result.get("done") else "failed",
        "query": result.get("query", ""),
        "sources": result.get("sources", []),
        "verified_claims": result.get("verified_claims", []),
        "report": result.get("report", ""),
        "presentation": result.get("presentation", ""),
        "error": result.get("error"),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/research")
async def list_research() -> ResearchList:
    repo = ResearchRepository()
    items = await repo.list_all()
    return ResearchList(researches=[ResearchResult(**r) for r in items])


@router.get("/research/{research_id}")
async def get_research(research_id: str) -> ResearchResult:
    repo = ResearchRepository()
    item = await repo.get(research_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Research not found")
    return ResearchResult(**item)
