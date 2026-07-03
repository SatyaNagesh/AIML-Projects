import logging

from src.agent.state import ResearchState
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

REPORT_SYSTEM = (
    "You are an expert report writer. Synthesize the research findings, "
    "verified claims, and organized sources into a comprehensive, well-structured report.\n\n"
    "The report must include:\n"
    "1. Executive Summary\n"
    "2. Introduction\n"
    "3. Key Findings (with evidence)\n"
    "4. Analysis\n"
    "5. Conclusion\n"
    "6. References (numbered, matching the sources provided)\n\n"
    "Write in markdown. Be thorough, objective, and cite sources inline as [1], [2], etc."
)


async def report_writer_node(state: ResearchState) -> dict:
    llm = LLMClient()

    if not state.extracted_content:
        return {"report": "No research content available to write a report."}

    sources_text = "\n".join(
        f"[{i+1}] {s.get('title', 'Untitled')} - {s.get('url', '')} "
        f"({s.get('type', 'web')})"
        for i, s in enumerate(state.sources[:30])
    )

    content_text = "\n\n".join(
        f"Source [{i+1}]: {c['title']}\n{c['content'][:2000]}"
        for i, c in enumerate(state.extracted_content[:15])
    )

    claims_text = "\n".join(
        f"- {c.get('claim', '')} (confidence: {c.get('confidence', 'N/A')}, "
        f"supported: {c.get('supported', '?')})"
        for c in state.verified_claims[:20]
    )

    report = await llm.generate(
        system=REPORT_SYSTEM,
        user=(
            f"Topic: {state.topic}\n\n"
            f"Search queries: {state.query}\n\n"
            f"--- Research Content ---\n{content_text}\n\n"
            f"--- Verified Claims ---\n{claims_text}\n\n"
            f"--- Sources ---\n{sources_text}\n\n"
            "Write the full report in markdown."
        ),
        temperature=0.4,
        max_tokens=8192,
    )

    logger.info("Report written (%d chars)", len(report))
    return {"report": report}
