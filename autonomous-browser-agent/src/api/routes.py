import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from src.agent.graph import build_agent_graph
from src.agent.state import AgentState
from src.api.schemas import TaskList, TaskRequest, TaskResult
from src.db.repository import TaskRepository

router = APIRouter(prefix="/api/v1", tags=["agent"])


@router.post("/tasks", status_code=201)
async def create_task(req: TaskRequest) -> dict:
    task_id = str(uuid.uuid4())
    repo = TaskRepository()
    await repo.create_task(
        task_id=task_id,
        task=req.task,
        url=req.url,
        status="queued",
    )
    state = AgentState(task=req.task, url=req.url)
    graph = build_agent_graph()
    result = await graph.ainvoke(state)

    await repo.update_task(
        task_id=task_id,
        status="completed" if result.get("done") else "failed",
        result=result.get("result"),
        error=result.get("error"),
        actions=[a.model_dump() for a in result.get("actions_taken", [])],
        steps=result.get("steps", []),
    )
    return {
        "task_id": task_id,
        "status": "completed" if result.get("done") else "failed",
        "result": result.get("result"),
        "error": result.get("error"),
        "steps": result.get("steps", []),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/tasks")
async def list_tasks() -> TaskList:
    repo = TaskRepository()
    tasks = await repo.list_tasks()
    return TaskList(tasks=[TaskResult(**t) for t in tasks])


@router.get("/tasks/{task_id}")
async def get_task(task_id: str) -> TaskResult:
    repo = TaskRepository()
    task = await repo.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResult(**task)
