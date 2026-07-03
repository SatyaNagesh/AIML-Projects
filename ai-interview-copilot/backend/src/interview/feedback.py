import logging

from src.interview.prompts import FEEDBACK_SYSTEM
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    def __init__(self) -> None:
        self.llm = LLMClient()

    async def generate(self, qa_pairs: list[dict]) -> dict:
        if not qa_pairs:
            return {"overall_score": 0, "summary": "No questions were answered."}

        qa_text = "\n\n".join(
            f"Q{i+1}: {pair['question']}\n"
            f"A: {pair['answer']}\n"
            f"Score: {pair.get('score', 'N/A')}\n"
            f"Strengths: {pair.get('strengths', [])}\n"
            f"Weaknesses: {pair.get('weaknesses', [])}"
            for i, pair in enumerate(qa_pairs)
        )

        result = await self.llm.generate_json(
            system=FEEDBACK_SYSTEM,
            user=f"Interview session Q&A:\n\n{qa_text}",
        )
        logger.info("Feedback generated, overall score: %s", result.get("overall_score"))
        return result
