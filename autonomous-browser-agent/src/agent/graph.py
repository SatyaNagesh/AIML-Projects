import logging
from datetime import UTC, datetime

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agent.nodes import agent_node, execute_node, should_continue
from src.agent.state import AgentState

logger = logging.getLogger(__name__)


def build_agent_graph() -> CompiledStateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("execute", execute_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"continue": "execute", "end": END},
    )
    workflow.add_edge("execute", "agent")

    return workflow.compile()


def run_sync(task: str, url: str | None = None) -> dict:
    graph = build_agent_graph()
    initial = AgentState(task=task, url=url)
    result = graph.invoke(initial)
    return {
        "task": task,
        "steps": result.get("steps", []),
        "actions": [a.model_dump() for a in result.get("actions_taken", [])],
        "result": result.get("result"),
        "error": result.get("error"),
        "done": result.get("done", False),
        "timestamp": datetime.now(UTC).isoformat(),
    }
