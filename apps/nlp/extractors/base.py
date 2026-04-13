from __future__ import annotations

from abc import ABC, abstractmethod

from models.extraction import ExtractionContext


class BaseExtractor(ABC):
    @abstractmethod
    async def extract(self, transcript: str, context: ExtractionContext) -> list:
        ...
