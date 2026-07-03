import json
import logging

from openai import AsyncOpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate(
        self,
        system: str,
        user: str,
        response_format: dict | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if response_format:
            kwargs["response_format"] = response_format

        resp = await self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    async def generate_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
    ) -> dict:
        raw = await self.generate(
            system=system,
            user=user,
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=4096,
        )
        return json.loads(raw)
