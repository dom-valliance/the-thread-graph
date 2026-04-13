from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from extractors.entity_extractor import EntityExtractor
from models.extraction import ExtractionContext, ExtractedEntity, PersonRef


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestEntityExtractor:
    @patch("extractors.entity_extractor.entity_graph")
    async def test_returns_valid_extracted_entities(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedEntity(id="ent-1", name="Sarah Chen", entity_type="person"),
            ExtractedEntity(id="ent-2", name="AI Agents", entity_type="topic"),
            ExtractedEntity(id="ent-3", name="McKinsey Digital", entity_type="player", matched_id="player-001"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = EntityExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 3
        assert all(isinstance(r, ExtractedEntity) for r in results)
        assert results[0].name == "Sarah Chen"
        assert results[0].entity_type == "person"
        assert results[0].matched_id is None
        assert results[2].matched_id == "player-001"
        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["transcript"] == sample_transcript
        assert call_args["context"] == extraction_context

    @patch("extractors.entity_extractor.entity_graph")
    async def test_returns_empty_list_when_no_results(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = EntityExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    @patch("extractors.entity_extractor.entity_graph")
    async def test_passes_known_topics_in_context(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_topics=["AI Agents", "Due Diligence"],
        )
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = EntityExtractor()
        await extractor.extract(sample_transcript, context)

        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["context"] == context
        assert "AI Agents" in call_args["context"].existing_topics
        assert "Due Diligence" in call_args["context"].existing_topics

    @patch("extractors.entity_extractor.entity_graph")
    async def test_passes_known_players_in_context(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_players=["McKinsey Digital", "Bain"],
        )
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = EntityExtractor()
        await extractor.extract(sample_transcript, context)

        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["context"] == context
        assert "McKinsey Digital" in call_args["context"].existing_players
        assert "Bain" in call_args["context"].existing_players

    @patch("extractors.entity_extractor.entity_graph")
    async def test_passes_known_people_in_context(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_people=[
                PersonRef(email="sarah@valliance.ai", name="Sarah Chen"),
            ],
        )
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = EntityExtractor()
        await extractor.extract(sample_transcript, context)

        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["context"] == context
        assert call_args["context"].existing_people[0].name == "Sarah Chen"
        assert call_args["context"].existing_people[0].email == "sarah@valliance.ai"
