from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extractors.entity_extractor import EntityExtractor
from models.extraction import ExtractionContext, ExtractedEntity, PersonRef


def _make_tool_response(entities: list[dict[str, object]]) -> SimpleNamespace:
    tool_block = SimpleNamespace(
        type="tool_use",
        name="store_entities",
        input={"entities": entities},
    )
    return SimpleNamespace(content=[tool_block])


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestEntityExtractor:
    async def test_returns_valid_extracted_entities(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_entities = [
            {"name": "Sarah Chen", "entity_type": "person"},
            {"name": "AI Agents", "entity_type": "topic"},
            {"name": "McKinsey Digital", "entity_type": "player", "matched_id": "player-001"},
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_entities)
        )

        extractor = EntityExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 3
        assert all(isinstance(r, ExtractedEntity) for r in results)
        assert results[0].name == "Sarah Chen"
        assert results[0].entity_type == "person"
        assert results[0].matched_id is None
        assert results[2].matched_id == "player-001"

    async def test_returns_empty_list_when_no_tool_use(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        text_block = SimpleNamespace(type="text", text="No entities found.")
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=SimpleNamespace(content=[text_block])
        )

        extractor = EntityExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    async def test_appends_known_topics_to_prompt(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_topics=["AI Agents", "Due Diligence"],
        )
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response([])
        )

        extractor = EntityExtractor(mock_anthropic_client)
        await extractor.extract(sample_transcript, context)

        call_args = mock_anthropic_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "AI Agents" in prompt
        assert "Due Diligence" in prompt

    async def test_appends_known_players_to_prompt(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_players=["McKinsey Digital", "Bain"],
        )
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response([])
        )

        extractor = EntityExtractor(mock_anthropic_client)
        await extractor.extract(sample_transcript, context)

        call_args = mock_anthropic_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "McKinsey Digital" in prompt
        assert "Bain" in prompt

    async def test_appends_known_people_to_prompt(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_people=[
                PersonRef(email="sarah@valliance.ai", name="Sarah Chen"),
            ],
        )
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response([])
        )

        extractor = EntityExtractor(mock_anthropic_client)
        await extractor.extract(sample_transcript, context)

        call_args = mock_anthropic_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Sarah Chen" in prompt
        assert "sarah@valliance.ai" in prompt
