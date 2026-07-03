from pydantic import BaseModel


class SessionCreate(BaseModel):
    resume: str = ""
    role: str = ""
    experience_level: str = "mid"


class QuestionResponse(BaseModel):
    session_id: str
    questions: list[dict]


class AnswerSubmit(BaseModel):
    session_id: str
    question_id: int
    question: str
    answer: str


class AnswerResponse(BaseModel):
    session_id: str
    question_id: int
    score: int
    strengths: list[str]
    weaknesses: list[str]
    suggested_answer: str
    tips: list[str]
    overall: str


class FeedbackRequest(BaseModel):
    session_id: str


class FeedbackResponse(BaseModel):
    session_id: str
    overall_score: int
    strengths: list[str]
    areas_to_improve: list[str]
    skill_gaps: list[str]
    recommended_resources: list[dict]
    summary: str


class SessionResult(BaseModel):
    session_id: str
    role: str = ""
    status: str
    question_count: int = 0
    average_score: float = 0.0
    created_at: str = ""
    updated_at: str = ""
