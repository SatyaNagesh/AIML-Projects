from src.agent.state import AgentState


def test_agent_state_defaults():
    state = AgentState(task="search for python jobs")
    assert state.task == "search for python jobs"
    assert state.max_steps == 25
    assert state.step_count == 0
    assert state.done is False


def test_agent_state_step_increment():
    state = AgentState(task="test")
    state.step_count += 1
    assert state.step_count == 1


def test_should_continue():
    state = AgentState(task="test")
    from src.agent.nodes import should_continue
    assert should_continue(state) == "continue"
    state.done = True
    assert should_continue(state) == "end"
    state.done = False
    state.step_count = 30
    assert should_continue(state) == "end"
