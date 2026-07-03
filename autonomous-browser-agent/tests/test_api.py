from src.api.schemas import TaskRequest, TaskResult


def test_task_request():
    req = TaskRequest(task="search google", url="https://google.com")
    assert req.task == "search google"
    assert req.url == "https://google.com"


def test_task_result():
    res = TaskResult(task_id="abc", task="test", result="ok", done=True)
    assert res.done is True
    assert res.result == "ok"
