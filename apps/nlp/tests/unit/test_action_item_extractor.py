from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extractors.action_item_extractor import ActionItemExtractor
from models.extraction import ExtractionContext, ExtractedActionItem, PersonRef


def _make_tool_response(action_items: list[dict[str, object]]) -> SimpleNamespace:
    tool_block = SimpleNamespace(
        type="tool_use",
        name="store_action_items",
        input={"action_items": action_items},
    )
    return SimpleNamespace(content=[tool_block])


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestActionItemExtractor:
    async def test_returns_valid_extracted_action_items(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_items = [
            {
                "text": "Write up the pilot results for the board",
                "assignee": "Marcus Webb",
                "due_date": "2026-04-01",
            },
            {
                "text": "Schedule legal review session",
                "assignee": "Sarah Chen",
            },
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_items)
        )

        extractor = ActionItemExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 2
        assert all(isinstance(r, ExtractedActionItem) for r in results)
        assert results[0].text == "Write up the pilot results for the board"
        assert results[0].assignee == "Marcus Webb"
        assert results[0].due_date == "2026-04-01"
        assert results[1].assignee == "Sarah Chen"
        assert results[1].due_date is None

    async def test_returns_empty_list_when_no_tool_use(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        text_block = SimpleNamespace(type="text", text="No action items found.")
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=SimpleNamespace(content=[text_block])
        )

        extractor = ActionItemExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    async def test_each_item_gets_unique_id(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_items = [
            {"text": "First task"},
            {"text": "Second task"},
            {"text": "Third task"},
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_items)
        )

        extractor = ActionItemExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        ids = [r.id for r in results]
        assert len(set(ids)) == 3

    async def test_optional_fields_default_to_none(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_items = [{"text": "A task with no assignee or date"}]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_items)
        )

        extractor = ActionItemExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results[0].assignee is None
        assert results[0].due_date is None

    async def test_appends_known_people_to_prompt(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_people=[
                PersonRef(email="marcus@valliance.ai", name="Marcus Webb"),
            ],
        )
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response([])
        )

        extractor = ActionItemExtractor(mock_anthropic_client)
        await extractor.extract(sample_transcript, context)

        call_args = mock_anthropic_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Marcus Webb" in prompt
        assert "marcus@valliance.ai" in prompt
