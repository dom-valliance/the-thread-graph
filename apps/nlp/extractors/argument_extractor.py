from __future__ import annotations

from models.extraction import ExtractionContext, ExtractedArgument
from extractors.base import BaseExtractor
from graphs.argument_graph import argument_graph


class ArgumentExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedArgument]:
        result = await argument_graph.ainvoke({
            "transcript": transcript,
            "context": context,
        })
        return result["results"]
