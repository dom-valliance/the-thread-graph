from __future__ import annotations

from models.enrichment import (
    ActionItemCreate,
    ArgumentCreate,
    EnrichmentResult,
    EvidenceCreate,
)
from repositories.enrichment_repository import EnrichmentRepository


class EnrichmentService:
    def __init__(self, repository: EnrichmentRepository) -> None:
        self._repo = repository

    async def create_arguments(
        self, arguments: list[ArgumentCreate]
    ) -> EnrichmentResult:
        items = [arg.model_dump() for arg in arguments]
        counts = await self._repo.batch_create_arguments(items)
        return EnrichmentResult(**counts)

    async def create_action_items(
        self, items: list[ActionItemCreate]
    ) -> EnrichmentResult:
        dicts = [item.model_dump() for item in items]
        counts = await self._repo.batch_create_action_items(dicts)
        return EnrichmentResult(**counts)

    async def create_evidence(
        self, evidence: list[EvidenceCreate]
    ) -> EnrichmentResult:
        items = [ev.model_dump() for ev in evidence]
        counts = await self._repo.batch_create_evidence(items)
        return EnrichmentResult(**counts)
