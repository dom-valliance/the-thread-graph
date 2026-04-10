from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from models.extraction import (
    ExtractionContext,
    ExtractionResult,
    ExtractedArgument,
    ExtractedActionItem,
    ExtractedEvidence,
    ExtractedEntity,
)
from models.session import SessionInput
from processors.transcript_processor import TranscriptProcessor


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


@pytest.fixture()
def session_input() -> SessionInput:
    return SessionInput(
        notion_id="session-001",
        title="AI Agents Discussion",
        transcript="Sarah: We should deploy AI agents for due diligence.",
    )


@pytest.fixture()
def mock_extractors() -> dict[str, AsyncMock]:
    return {
        "argument": AsyncMock(),
        "action_item": AsyncMock(),
        "evidence": AsyncMock(),
        "entity": AsyncMock(),
    }


class TestTranscriptProcessor:
    async def test_calls_all_extractors_and_returns_result(
        self,
        session_input: SessionInput,
        extraction_context: ExtractionContext,
        mock_extractors: dict[str, AsyncMock],
    ) -> None:
        arguments = [
            ExtractedArgument(
                id="arg-1", text="AI is faster", sentiment="supports",
                relationship_type="SUPPORTS",
            ),
        ]
        action_items = [
            ExtractedActionItem(id="ai-1", text="Write pilot report"),
        ]
        evidence = [
            ExtractedEvidence(id="ev-1", text="400 docs in 2 hours", type="data_point"),
        ]
        entities = [
            ExtractedEntity(name="Sarah Chen", entity_type="person"),
        ]

        mock_extractors["argument"].extract = AsyncMock(return_value=arguments)
        mock_extractors["action_item"].extract = AsyncMock(return_value=action_items)
        mock_extractors["evidence"].extract = AsyncMock(return_value=evidence)
        mock_extractors["entity"].extract = AsyncMock(return_value=entities)

        processor = TranscriptProcessor(
            argument_extractor=mock_extractors["argument"],
            action_item_extractor=mock_extractors["action_item"],
            evidence_extractor=mock_extractors["evidence"],
            entity_extractor=mock_extractors["entity"],
        )

        result = await processor.process(session_input, extraction_context)

        assert isinstance(result, ExtractionResult)
        assert len(result.arguments) == 1
        assert len(result.action_items) == 1
        assert len(result.evidence) == 1
        assert len(result.entities) == 1

        mock_extractors["argument"].extract.assert_awaited_once_with(
            session_input.transcript, extraction_context
        )
        mock_extractors["action_item"].extract.assert_awaited_once_with(
            session_input.transcript, extraction_context
        )

    async def test_deduplicates_entities_by_type_and_name(
        self,
        session_input: SessionInput,
        extraction_context: ExtractionContext,
        mock_extractors: dict[str, AsyncMock],
    ) -> None:
        entities = [
            ExtractedEntity(name="Sarah Chen", entity_type="person"),
            ExtractedEntity(name="sarah chen", entity_type="person"),
            ExtractedEntity(name="Sarah Chen", entity_type="topic"),
        ]

        mock_extractors["argument"].extract = AsyncMock(return_value=[])
        mock_extractors["action_item"].extract = AsyncMock(return_value=[])
        mock_extractors["evidence"].extract = AsyncMock(return_value=[])
        mock_extractors["entity"].extract = AsyncMock(return_value=entities)

        processor = TranscriptProcessor(
            argument_extractor=mock_extractors["argument"],
            action_item_extractor=mock_extractors["action_item"],
            evidence_extractor=mock_extractors["evidence"],
            entity_extractor=mock_extractors["entity"],
        )

        result = await processor.process(session_input, extraction_context)

        assert len(result.entities) == 2
        types = {e.entity_type for e in result.entities}
        assert types == {"person", "topic"}

    async def test_handles_empty_results_from_all_extractors(
        self,
        session_input: SessionInput,
        extraction_context: ExtractionContext,
        mock_extractors: dict[str, AsyncMock],
    ) -> None:
        mock_extractors["argument"].extract = AsyncMock(return_value=[])
        mock_extractors["action_item"].extract = AsyncMock(return_value=[])
        mock_extractors["evidence"].extract = AsyncMock(return_value=[])
        mock_extractors["entity"].extract = AsyncMock(return_value=[])

        processor = TranscriptProcessor(
            argument_extractor=mock_extractors["argument"],
            action_item_extractor=mock_extractors["action_item"],
            evidence_extractor=mock_extractors["evidence"],
            entity_extractor=mock_extractors["entity"],
        )

        result = await processor.process(session_input, extraction_context)

        assert result.arguments == []
        assert result.action_items == []
        assert result.evidence == []
        assert result.entities == []
