from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from extractors.argument_extractor import ArgumentExtractor
from models.extraction import ExtractionContext, ExtractedArgument


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestArgumentExtractor:
    @patch("extractors.argument_extractor.argument_graph")
    async def test_returns_valid_extracted_arguments(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedArgument(
                id="arg-1",
                text="AI agents process documents faster than humans",
                sentiment="supports",
                strength="strong",
                speaker="Marcus Webb",
                relationship_type="SUPPORTS",
            ),
            ExtractedArgument(
                id="arg-2",
                text="The miss rate in due diligence is a concern",
                sentiment="challenges",
                strength="moderate",
                speaker="Priya Patel",
                relationship_type="CHALLENGES",
            ),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = ArgumentExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 2
        assert all(isinstance(r, ExtractedArgument) for r in results)
        assert results[0].text == "AI agents process documents faster than humans"
        assert results[0].sentiment == "supports"
        assert results[0].strength == "strong"
        assert results[0].speaker == "Marcus Webb"
        assert results[0].relationship_type == "SUPPORTS"
        assert results[1].sentiment == "challenges"
        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["transcript"] == sample_transcript
        assert call_args["context"] == extraction_context

    @patch("extractors.argument_extractor.argument_graph")
    async def test_returns_empty_list_when_no_results(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = ArgumentExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    @patch("extractors.argument_extractor.argument_graph")
    async def test_each_argument_gets_unique_id(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedArgument(id="arg-1", text="First argument", sentiment="neutral", relationship_type="SUPPORTS"),
            ExtractedArgument(id="arg-2", text="Second argument", sentiment="neutral", relationship_type="SUPPORTS"),
            ExtractedArgument(id="arg-3", text="Third argument", sentiment="neutral", relationship_type="SUPPORTS"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = ArgumentExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        ids = [r.id for r in results]
        assert len(set(ids)) == 3

    @patch("extractors.argument_extractor.argument_graph")
    async def test_optional_fields_default_to_none(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedArgument(id="arg-1", text="An argument", sentiment="neutral", relationship_type="SUPPORTS"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = ArgumentExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results[0].strength is None
        assert results[0].speaker is None
        assert results[0].position_id is None
