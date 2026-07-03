from src.agent.state import ResearchState


def test_research_state_defaults():
    state = ResearchState(topic="quantum computing")
    assert state.topic == "quantum computing"
    assert state.next_agent == "research"
    assert state.done is False
    assert state.sources == []


def test_research_state_accumulates():
    state = ResearchState(topic="test")
    state.search_results.append({"title": "result 1"})
    state.extracted_content.append({"title": "content 1"})
    assert len(state.search_results) == 1
    assert len(state.extracted_content) == 1


def test_supervisor_router():
    from src.agent.graph import router
    state = ResearchState(topic="test", next_agent="factcheck")
    assert router(state) == "factcheck"
    state.next_agent = "report_writer"
    assert router(state) == "report_writer"
    state.next_agent = "unknown"
    assert router(state) == "research"
    state.done = True
    assert router(state) == "end"
