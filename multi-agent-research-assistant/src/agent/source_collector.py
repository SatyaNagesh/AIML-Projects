import logging

from src.agent.state import ResearchState
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

SOURCE_SYSTEM = (
    "You are a source collector and citation organizer. "
    "Given the research content and verified claims, organize all sources "
    "into properly formatted citations categorized by type "
    "(article, documentation, blog, news, academic).\n\n"
    "Return a JSON object:\n"
    '{"sources": [{"title": "...", "url": "...", "type": "...", '
    '"relevance": "high|medium|low", "key_findings": ["..."]}]}'
)


async def source_collector_node(state: ResearchState) -> dict:
    llm = LLMClient()

    if not state.extracted_content:
        return {"sources": []}

    content_text = "\n\n".join(
        f"[{i+1}] {c['title']} ({c['source_url']})\n{c['content'][:1000]}"
        for i, c in enumerate(state.extracted_content)
    )

    result = await llm.generate_json(
        system=SOURCE_SYSTEM,
        user=(
            f"Topic: {state.topic}\n\n"
            f"Research content:\n{content_text}\n\n"
            f"Verified claims:\n{state.verified_claims}"
        ),
    )
    sources = result.get("sources", [])
    logger.info("Source collector: %d sources organized", len(sources))
    return {"sources": sources}
