from pydantic import BaseModel


class LLMResponse(BaseModel):
    reasoning: str = ""
    action: str = ""
    parameters: dict = {}
