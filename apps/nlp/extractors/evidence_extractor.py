from __future__ import annotations

from models.extraction import ExtractionContext, ExtractedEvidence
from extractors.base import BaseExtractor
from graphs.evidence_graph import evidence_graph


class EvidenceExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedEvidence]:
        result = await evidence_graph.ainvoke({
            "transcript": transcript,
            "context": context,
        })
        return result["results"]
