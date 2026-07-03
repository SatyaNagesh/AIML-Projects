import json
import logging

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.state import AgentState
from src.browser.controller import BrowserController
from src.browser.models import BrowserAction
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


_controller: BrowserController | None = None


async def _get_browser() -> BrowserController:
    global _controller
    if _controller is None:
        _controller = await BrowserController.create()
    return _controller


def _build_context(state: AgentState) -> str:
    parts = [f"Task: {state.task}"]
    if state.url:
        parts.append(f"Current URL: {state.url}")
    if state.current_snapshot:
        parts.append(f"\nPage content:\n{state.current_snapshot.dom_summary[:3000]}")
        if state.current_snapshot.form_fields:
            ff = json.dumps(state.current_snapshot.form_fields, indent=2)
            parts.append(f"\nForm fields:\n{ff}")
        if state.current_snapshot.links:
            links = state.current_snapshot.links[:20]
            parts.append(f"\nLinks ({len(links)}): {links}")
        if state.current_snapshot.interactable:
            parts.append(f"\nInteractable elements: {state.current_snapshot.interactable[:30]}")
    if state.steps:
        parts.append(f"\nSteps completed: {state.steps}")
    if state.actions_taken:
        last = state.actions_taken[-3:]
        parts.append(f"\nRecent actions: {[a.model_dump() for a in last]}")
    parts.append(f"\nStep {state.step_count + 1}/{state.max_steps}")
    return "\n".join(parts)


async def agent_node(state: AgentState) -> dict:
    llm = _get_llm()
    context = _build_context(state)
    response = await llm.generate_action(context)
    logger.info("LLM action: %s", response.get("action"))
    step_summary = response.get("reasoning", response.get("action", ""))
    return {"steps": [step_summary]}


async def execute_node(state: AgentState) -> dict:
    updates: dict = {"step_count": state.step_count + 1}
    llm = _get_llm()
    context = _build_context(state)
    response = await llm.generate_action(context)
    action_raw = response.get("action", "done")
    reasoning = response.get("reasoning", "")
    params = response.get("parameters", {})

    try:
        browser = await _get_browser()
        action = BrowserAction(action=action_raw, parameters=params, reasoning=reasoning)
        result = await browser.execute(action)

        snapshot = result.pop("snapshot", None)

        updates.setdefault("actions_taken", []).append(action)
        updates["current_snapshot"] = snapshot

        if action_raw == "navigate" and params.get("url"):
            updates["url"] = params["url"]

        if action_raw == "done":
            updates["done"] = True
            updates["result"] = params.get("result", "Task completed")

        if snapshot:
            updates.setdefault("snapshots", []).append(snapshot)
            updates["current_snapshot"] = snapshot

        updates["extracted_data"] = result.get("extracted_data")

    except Exception as e:
        logger.exception("Browser action failed")
        updates["error"] = str(e)
        updates["actions_taken"] = [
            BrowserAction(
                action="error",
                parameters={"message": str(e)},
                reasoning=reasoning,
            )
        ]

    return updates


def should_continue(state: AgentState) -> str:
    if state.done or state.error or state.step_count >= state.max_steps:
        return "end"
    return "continue"


_llm: LLMClient | None = None


def _get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient(system_prompt=SYSTEM_PROMPT)
    return _llm
