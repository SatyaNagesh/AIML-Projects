import logging

from langgraph.graph import END, StateGraph

from src.agent.factcheck_agent import factcheck_node
from src.agent.presentation_agent import presentation_node
from src.agent.report_writer import report_writer_node
from src.agent.research_agent import research_node
from src.agent.source_collector import source_collector_node
from src.agent.state import ResearchState
from src.agent.supervisor import supervisor_node

logger = logging.getLogger(__name__)

NODE_MAP = {
    "research": research_node,
    "factcheck": factcheck_node,
    "source_collector": source_collector_node,
    "report_writer": report_writer_node,
    "presentation_creator": presentation_node,
}


def router(state: ResearchState) -> str:
    if state.done:
        return "end"
    agent = state.next_agent
    if agent in NODE_MAP or agent == "supervisor":
        return agent
    return "research"


def build_research_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("supervisor", supervisor_node)
    for name, node_fn in NODE_MAP.items():
        workflow.add_node(name, node_fn)

    workflow.set_entry_point("supervisor")

    for name in list(NODE_MAP) + ["supervisor"]:
        workflow.add_conditional_edges(name, router, {
            **{n: n for n in NODE_MAP},
            "supervisor": "supervisor",
            "end": END,
        })

    return workflow.compile()
