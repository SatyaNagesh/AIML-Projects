import logging

from src.interview.prompts import QUESTION_SYSTEM
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


class QuestionGenerator:
    def __init__(self) -> None:
        self.llm = LLMClient()

    async def generate(
        self,
        resume: str = "",
        role: str = "",
        experience_level: str = "mid",
        previous_questions: list[str] | None = None,
        count: int = 5,
    ) -> list[dict]:
        context = (
            f"Job Role: {role or 'Not specified'}\n"
            f"Experience Level: {experience_level}\n"
            f"Resume:\n{resume[:2000] or 'No resume provided'}\n"
        )
        if previous_questions:
            context += "\nAlready asked:\n" + "\n".join(f"- {q}" for q in previous_questions)

        result = await self.llm.generate_json(
            system=QUESTION_SYSTEM,
            user=f"Generate {count} interview questions for:\n\n{context}",
        )
        questions = result.get("questions", [])
        logger.info("Generated %d questions", len(questions))
        return questions
