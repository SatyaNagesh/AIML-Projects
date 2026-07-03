from src.interview.engine import InterviewEngine
from src.interview.evaluator import AnswerEvaluator
from src.interview.feedback import FeedbackGenerator
from src.interview.question_generator import QuestionGenerator


def test_question_generator_init():
    qg = QuestionGenerator()
    assert qg is not None


def test_evaluator_init():
    ev = AnswerEvaluator()
    assert ev is not None


def test_feedback_init():
    fg = FeedbackGenerator()
    assert fg is not None


def test_engine_init():
    eng = InterviewEngine()
    assert eng is not None
