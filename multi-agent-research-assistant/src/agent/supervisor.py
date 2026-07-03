import logging

from src.agent.state import ResearchState
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM = (
    "You are a research supervisor orchestrating a team of specialized AI agents. "
    "Given a research topic and the current state, decide which agent to call next.\n\n"
    "Agents available:\n"
    "- research: Search the web and extract content on the topic\n"
    "- factcheck: Cross-verify facts and claims from research\n"
    "- source_collector: Organize and format all sources with citations\n"
    "- report_writer: Write the final detailed report\n"
    "- presentation_creator: Create slide-deck content from the report\n"
    "- done: All work is complete\n\n"
    "Respond with JSON: {\"next\": \"<agent_name>\"}"
)


async def supervisor_node(state: ResearchState) -> dict:
    llm = LLMClient()

    context = (
        f"Topic: {state.topic}\n"
        f"Search queries used: {state.query or 'not yet'}\n"
        f"Content extracted: {len(state.extracted_content)} items\n"
        f"Claims verified: {len(state.verified_claims)}\n"
        f"Sources organized: {len(state.sources)}\n"
        f"Report written: {'yes' if state.report else 'no'}\n"
        f"Presentation created: {'yes' if state.presentation else 'no'}\n"
    )

    decision = await llm.generate_json(
        system=SUPERVISOR_SYSTEM,
        user=context,
    )
    next_agent = decision.get("next", "research")

    updates: dict = {"next_agent": next_agent}
    if next_agent == "done":
        updates["done"] = True
    return updates
