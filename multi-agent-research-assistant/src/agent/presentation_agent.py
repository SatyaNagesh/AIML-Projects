import logging

from src.agent.state import ResearchState
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

PRESENTATION_SYSTEM = (
    "You are a presentation designer. Convert the research report into "
    "a structured slide deck outline. Each slide should have a title, "
    "3-5 bullet points, and speaker notes.\n\n"
    "Return the presentation in this format:\n\n"
    "## Slide 1: Title\n"
    "- Bullet point\n"
    "- Bullet point\n"
    "Notes: Speaker notes here\n\n"
    "Create 8-12 slides covering:\n"
    "1. Title slide with topic\n"
    "2. Agenda\n"
    "3. Executive Summary\n"
    "4-7. Key Findings (1-2 slides per major finding)\n"
    "8. Analysis\n"
    "9. Conclusion\n"
    "10. References / Q&A"
)


async def presentation_node(state: ResearchState) -> dict:
    llm = LLMClient()

    if not state.report:
        return {"presentation": "No report available to create a presentation."}

    presentation = await llm.generate(
        system=PRESENTATION_SYSTEM,
        user=(
            f"Topic: {state.topic}\n\n"
            f"Research Report:\n{state.report[:8000]}\n\n"
            "Create the slide deck outline."
        ),
        temperature=0.4,
        max_tokens=4096,
    )

    logger.info("Presentation created (%d chars)", len(presentation))
    return {"presentation": presentation}
