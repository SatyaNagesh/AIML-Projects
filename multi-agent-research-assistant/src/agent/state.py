import operator
from dataclasses import dataclass, field
from typing import Annotated


@dataclass
class ResearchState:
    topic: str
    query: str = ""
    next_agent: str = "research"

    search_results: Annotated[list[dict], operator.add] = field(default_factory=list)
    extracted_content: Annotated[list[dict], operator.add] = field(default_factory=list)
    verified_claims: Annotated[list[dict], operator.add] = field(default_factory=list)
    sources: Annotated[list[dict], operator.add] = field(default_factory=list)
    report_sections: Annotated[list[dict], operator.add] = field(default_factory=list)

    report: str = ""
    presentation: str = ""
    error: str | None = None
    done: bool = False
