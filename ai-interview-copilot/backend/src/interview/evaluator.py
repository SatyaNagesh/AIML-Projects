import logging

from src.interview.prompts import EVALUATION_SYSTEM
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


class AnswerEvaluator:
    def __init__(self) -> None:
        self.llm = LLMClient()

    async def evaluate(self, question: str, answer: str) -> dict:
        result = await self.llm.generate_json(
            system=EVALUATION_SYSTEM,
            user=(
                f"Question: {question}\n\n"
                f"Candidate's Answer:\n{answer}"
            ),
        )
        logger.info("Evaluation score: %s", result.get("score"))
        return result
