from __future__ import annotations

from models.extraction import ExtractionContext, ExtractedEntity
from extractors.base import BaseExtractor
from graphs.entity_graph import entity_graph


class EntityExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedEntity]:
        result = await entity_graph.ainvoke({
            "transcript": transcript,
            "context": context,
        })
        return result["results"]
