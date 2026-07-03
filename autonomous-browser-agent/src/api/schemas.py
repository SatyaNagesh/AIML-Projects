from pydantic import BaseModel


class TaskRequest(BaseModel):
    task: str
    url: str | None = None


class TaskResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str = ""


class TaskResult(BaseModel):
    task_id: str
    task: str
    steps: list[str] = []
    actions: list[dict] = []
    result: str | None = None
    error: str | None = None
    done: bool = False
    timestamp: str = ""


class TaskList(BaseModel):
    tasks: list[TaskResult]
