import operator
from dataclasses import dataclass, field
from typing import Annotated

from src.browser.models import BrowserAction, BrowserSnapshot


@dataclass
class AgentState:
    task: str
    url: str | None = None

    steps: Annotated[list[str], operator.add] = field(default_factory=list)
    actions_taken: Annotated[list[BrowserAction], operator.add] = field(default_factory=list)
    snapshots: Annotated[list[BrowserSnapshot], operator.add] = field(default_factory=list)

    current_snapshot: BrowserSnapshot | None = None
    extracted_data: dict | None = None

    max_steps: int = 25
    step_count: int = 0
    done: bool = False
    error: str | None = None
    result: str | None = None
