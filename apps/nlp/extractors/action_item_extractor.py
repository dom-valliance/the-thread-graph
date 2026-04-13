from __future__ import annotations

from models.extraction import ExtractionContext, ExtractedActionItem
from extractors.base import BaseExtractor
from graphs.action_item_graph import action_item_graph


class ActionItemExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedActionItem]:
        result = await action_item_graph.ainvoke({
            "transcript": transcript,
            "context": context,
        })
        return result["results"]
