from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extractors.argument_extractor import ArgumentExtractor
from models.extraction import ExtractionContext, ExtractedArgument


def _make_tool_response(arguments: list[dict[str, object]]) -> SimpleNamespace:
    """Build a mock Anthropic API response with tool_use content."""
    tool_block = SimpleNamespace(
        type="tool_use",
        name="store_arguments",
        input={"arguments": arguments},
    )
    return SimpleNamespace(content=[tool_block])


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestArgumentExtractor:
    async def test_returns_valid_extracted_arguments(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_arguments = [
            {
                "text": "AI agents process documents faster than humans",
                "sentiment": "supports",
                "strength": "strong",
                "speaker": "Marcus Webb",
                "relationship_type": "SUPPORTS",
            },
            {
                "text": "The miss rate in due diligence is a concern",
                "sentiment": "challenges",
                "strength": "moderate",
                "speaker": "Priya Patel",
                "relationship_type": "CHALLENGES",
            },
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_arguments)
        )

        extractor = ArgumentExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 2
        assert all(isinstance(r, ExtractedArgument) for r in results)
        assert results[0].text == "AI agents process documents faster than humans"
        assert results[0].sentiment == "supports"
        assert results[0].strength == "strong"
        assert results[0].speaker == "Marcus Webb"
        assert results[0].relationship_type == "SUPPORTS"
        assert results[1].sentiment == "challenges"

    async def test_returns_empty_list_when_no_tool_use(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        text_block = SimpleNamespace(type="text", text="No arguments found.")
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=SimpleNamespace(content=[text_block])
        )

        extractor = ArgumentExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    async def test_each_argument_gets_unique_id(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_arguments = [
            {"text": "First argument", "sentiment": "neutral", "relationship_type": "SUPPORTS"},
            {"text": "Second argument", "sentiment": "neutral", "relationship_type": "SUPPORTS"},
            {"text": "Third argument", "sentiment": "neutral", "relationship_type": "SUPPORTS"},
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_arguments)
        )

        extractor = ArgumentExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        ids = [r.id for r in results]
        assert len(set(ids)) == 3

    async def test_optional_fields_default_to_none(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_arguments = [
            {"text": "An argument", "sentiment": "neutral", "relationship_type": "SUPPORTS"},
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_arguments)
        )

        extractor = ArgumentExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results[0].strength is None
        assert results[0].speaker is None
        assert results[0].position_id is None
