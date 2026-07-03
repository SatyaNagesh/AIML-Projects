import json
import logging

from openai import AsyncOpenAI

from src.config import settings
from src.llm.schemas import LLMResponse

logger = logging.getLogger(__name__)

ACTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "browser_action",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string", "description": "Brief reasoning for this action"},
                "action": {
                    "type": "string",
                    "enum": [
                        "navigate", "click", "fill", "select",
                        "screenshot", "extract", "scroll", "wait", "done",
                    ],
                    "description": "The browser action to take",
                },
                "parameters": {
                    "type": "object",
                    "description": "Action parameters (url, selector, value, etc.)",
                    "additionalProperties": True,
                },
            },
            "required": ["reasoning", "action", "parameters"],
            "additionalProperties": False,
        },
    },
}


class LLMClient:
    def __init__(self, system_prompt: str = "") -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.system_prompt = system_prompt

    async def generate_action(self, context: str) -> LLMResponse:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context},
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format=ACTION_SCHEMA,
                temperature=0.2,
                max_tokens=512,
            )
            raw = response.choices[0].message.content or "{}"
            parsed = json.loads(raw)
            return LLMResponse(**parsed)
        except Exception as e:
            logger.exception("LLM call failed")
            return LLMResponse(
                reasoning="LLM error", action="done",
                parameters={"result": f"Error: {e}"},
            )

    async def decompose_task(self, task: str) -> list[str]:
        messages = [
            {
                "role": "system",
                "content": (
                    "Break the task into sequential browser steps. "
                    "Return a JSON array of strings."
                ),
            },
            {"role": "user", "content": task},
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1024,
            )
            data = json.loads(response.choices[0].message.content or "[]")
            if isinstance(data, dict):
                return data.get("steps", data.get("plan", []))
            return data if isinstance(data, list) else []
        except Exception:
            return [task]
