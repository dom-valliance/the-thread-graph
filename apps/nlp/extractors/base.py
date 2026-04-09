from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import anthropic

from models.extraction import ExtractionContext


class BaseExtractor(ABC):
    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    @abstractmethod
    async def extract(self, transcript: str, context: ExtractionContext) -> list:
        ...

    def _load_prompt(self, prompt_name: str) -> str:
        prompt_path = Path(__file__).parent.parent / "prompts" / f"{prompt_name}.txt"
        return prompt_path.read_text()

    def _build_prompt(self, template: str, transcript: str, context: ExtractionContext) -> str:
        return (
            template.replace("{{TRANSCRIPT}}", transcript)
            .replace("{{ARC_NAME}}", context.arc_name or "Unknown")
            .replace("{{SESSION_ID}}", context.session_id)
        )
