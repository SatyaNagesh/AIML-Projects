import logging

from src.interview.evaluator import AnswerEvaluator
from src.interview.feedback import FeedbackGenerator
from src.interview.question_generator import QuestionGenerator

logger = logging.getLogger(__name__)


class InterviewEngine:
    def __init__(self) -> None:
        self.question_gen = QuestionGenerator()
        self.evaluator = AnswerEvaluator()
        self.feedback_gen = FeedbackGenerator()

    async def generate_questions(
        self,
        resume: str = "",
        role: str = "",
        level: str = "mid",
        count: int = 5,
    ) -> list[dict]:
        return await self.question_gen.generate(
            resume=resume, role=role, experience_level=level, count=count,
        )

    async def evaluate_answer(self, question: str, answer: str) -> dict:
        return await self.evaluator.evaluate(question, answer)

    async def generate_feedback(self, qa_pairs: list[dict]) -> dict:
        return await self.feedback_gen.generate(qa_pairs)
