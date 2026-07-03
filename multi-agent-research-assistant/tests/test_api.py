from src.api.schemas import ResearchRequest, ResearchResult


def test_research_request():
    req = ResearchRequest(topic="AI regulation")
    assert req.topic == "AI regulation"


def test_research_result():
    res = ResearchResult(
        research_id="abc",
        topic="test",
        report="# Report",
        done=True,
    )
    assert res.done is True
    assert res.report == "# Report"
