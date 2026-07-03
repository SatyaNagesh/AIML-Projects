import logging
import os
from io import BytesIO

from openai import AsyncOpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    def __init__(self) -> None:
        key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY", "sk-test")
        self.client = AsyncOpenAI(api_key=key)

    async def transcribe(self, audio_bytes: bytes) -> str:
        buffer = BytesIO(audio_bytes)
        buffer.name = "audio.webm"
        transcript = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            response_format="text",
        )
        return transcript.strip()

    async def transcribe_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            return await self.transcribe(f.read())
