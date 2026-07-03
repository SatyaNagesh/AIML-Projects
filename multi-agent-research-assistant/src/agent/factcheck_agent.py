import logging

from src.agent.state import ResearchState
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

FACTCHECK_SYSTEM = (
    "You are a fact-checking agent. Review the provided research content and claims. "
    "For each key claim found in the content, determine:\n"
    "1. Whether it is supported by the provided sources\n"
    "2. How confident you are (high / medium / low)\n"
    "3. Any contradictions or gaps\n\n"
    "Return a JSON object:\n"
    '{"claims": [{"claim": "...", "supported": true/false, '
    '"confidence": "high|medium|low", "source_url": "...", '
    '"notes": "..."}]}'
)


async def factcheck_node(state: ResearchState) -> dict:
    llm = LLMClient()

    content_text = "\n\n".join(
        f"[{i+1}] {c['title']}\n{c['content'][:1500]}"
        for i, c in enumerate(state.extracted_content[:10])
    )
    if not content_text.strip():
        return {"verified_claims": []}

    result = await llm.generate_json(
        system=FACTCHECK_SYSTEM,
        user=(
            f"Topic: {state.topic}\n\n"
            f"Research content to verify:\n{content_text}"
        ),
    )
    claims = result.get("claims", [])
    logger.info("Fact-check: %d claims evaluated", len(claims))
    return {"verified_claims": claims}
