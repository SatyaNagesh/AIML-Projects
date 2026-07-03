from pydantic import BaseModel


class BrowserAction(BaseModel):
    action: str
    parameters: dict = {}
    reasoning: str = ""


class BrowserSnapshot(BaseModel):
    url: str
    title: str
    dom_summary: str
    form_fields: list[dict] = []
    links: list[str] = []
    interactable: list[str] = []
