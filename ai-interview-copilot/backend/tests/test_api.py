from src.api.schemas import AnswerSubmit, FeedbackRequest, SessionCreate
from src.speech.whisper import WhisperTranscriber


def test_session_create():
    req = SessionCreate(role="Software Engineer", resume="Python, React", experience_level="mid")
    assert req.role == "Software Engineer"
    assert req.experience_level == "mid"


def test_answer_submit():
    req = AnswerSubmit(
        session_id="abc", question_id=1,
        question="What is OOP?",
        answer="Object-oriented programming...",
    )
    assert req.question == "What is OOP?"
    assert req.question_id == 1


def test_feedback_request():
    req = FeedbackRequest(session_id="abc")
    assert req.session_id == "abc"


def test_whisper_init():
    t = WhisperTranscriber()
    assert t is not None
