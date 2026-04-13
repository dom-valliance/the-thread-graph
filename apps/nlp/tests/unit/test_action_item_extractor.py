from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from extractors.action_item_extractor import ActionItemExtractor
from models.extraction import ExtractionContext, ExtractedActionItem, PersonRef


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestActionItemExtractor:
    @patch("extractors.action_item_extractor.action_item_graph")
    async def test_returns_valid_extracted_action_items(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedActionItem(
                id="ai-1",
                text="Write up the pilot results for the board",
                assignee="Marcus Webb",
                due_date="2026-04-01",
            ),
            ExtractedActionItem(
                id="ai-2",
                text="Schedule legal review session",
                assignee="Sarah Chen",
            ),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = ActionItemExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 2
        assert all(isinstance(r, ExtractedActionItem) for r in results)
        assert results[0].text == "Write up the pilot results for the board"
        assert results[0].assignee == "Marcus Webb"
        assert results[0].due_date == "2026-04-01"
        assert results[1].assignee == "Sarah Chen"
        assert results[1].due_date is None
        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["transcript"] == sample_transcript
        assert call_args["context"] == extraction_context

    @patch("extractors.action_item_extractor.action_item_graph")
    async def test_returns_empty_list_when_no_results(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = ActionItemExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    @patch("extractors.action_item_extractor.action_item_graph")
    async def test_each_item_gets_unique_id(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedActionItem(id="ai-1", text="First task"),
            ExtractedActionItem(id="ai-2", text="Second task"),
            ExtractedActionItem(id="ai-3", text="Third task"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = ActionItemExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        ids = [r.id for r in results]
        assert len(set(ids)) == 3

    @patch("extractors.action_item_extractor.action_item_graph")
    async def test_optional_fields_default_to_none(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [ExtractedActionItem(id="ai-1", text="A task with no assignee or date")]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = ActionItemExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results[0].assignee is None
        assert results[0].due_date is None

    @patch("extractors.action_item_extractor.action_item_graph")
    async def test_passes_known_people_in_context(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_people=[
                PersonRef(email="marcus@valliance.ai", name="Marcus Webb"),
            ],
        )
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = ActionItemExtractor()
        await extractor.extract(sample_transcript, context)

        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["context"] == context
        assert call_args["context"].existing_people[0].name == "Marcus Webb"
        assert call_args["context"].existing_people[0].email == "marcus@valliance.ai"
