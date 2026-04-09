from __future__ import annotations

from extractors.argument_extractor import ArgumentExtractor
from extractors.action_item_extractor import ActionItemExtractor
from extractors.evidence_extractor import EvidenceExtractor
from extractors.entity_extractor import EntityExtractor
from models.extraction import ExtractionContext, ExtractionResult
from models.session import SessionInput


class TranscriptProcessor:
    def __init__(
        self,
        argument_extractor: ArgumentExtractor,
        action_item_extractor: ActionItemExtractor,
        evidence_extractor: EvidenceExtractor,
        entity_extractor: EntityExtractor,
    ) -> None:
        self._argument_extractor = argument_extractor
        self._action_item_extractor = action_item_extractor
        self._evidence_extractor = evidence_extractor
        self._entity_extractor = entity_extractor

    async def process(
        self, session: SessionInput, context: ExtractionContext
    ) -> ExtractionResult:
        arguments = await self._argument_extractor.extract(session.transcript, context)
        action_items = await self._action_item_extractor.extract(session.transcript, context)
        evidence = await self._evidence_extractor.extract(session.transcript, context)
        entities = await self._entity_extractor.extract(session.transcript, context)

        entities = self._deduplicate_entities(entities)

        return ExtractionResult(
            arguments=arguments,
            action_items=action_items,
            evidence=evidence,
            entities=entities,
        )

    def _deduplicate_entities(self, entities: list) -> list:
        seen: dict[str, object] = {}
        for entity in entities:
            key = f"{entity.entity_type}:{entity.name.lower()}"
            if key not in seen:
                seen[key] = entity
        return list(seen.values())
