from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from extractors.evidence_extractor import EvidenceExtractor
from models.extraction import ExtractionContext, ExtractedEvidence, PositionRef


def _make_tool_response(evidence: list[dict[str, object]]) -> SimpleNamespace:
    tool_block = SimpleNamespace(
        type="tool_use",
        name="store_evidence",
        input={"evidence": evidence},
    )
    return SimpleNamespace(content=[tool_block])


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestEvidenceExtractor:
    async def test_returns_valid_extracted_evidence(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_evidence = [
            {
                "text": "400 documents processed in 2 hours vs 3-4 days manually",
                "type": "data_point",
                "position_id": "pos-001",
            },
            {
                "text": "94% accuracy rate on document review",
                "type": "data_point",
            },
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_evidence)
        )

        extractor = EvidenceExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 2
        assert all(isinstance(r, ExtractedEvidence) for r in results)
        assert results[0].text == "400 documents processed in 2 hours vs 3-4 days manually"
        assert results[0].type == "data_point"
        assert results[0].position_id == "pos-001"
        assert results[1].position_id is None

    async def test_returns_empty_list_when_no_tool_use(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        text_block = SimpleNamespace(type="text", text="No evidence found.")
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=SimpleNamespace(content=[text_block])
        )

        extractor = EvidenceExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    async def test_each_item_gets_unique_id(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_evidence = [
            {"text": "First evidence", "type": "citation"},
            {"text": "Second evidence", "type": "anecdote"},
            {"text": "Third evidence", "type": "case_study"},
        ]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_evidence)
        )

        extractor = EvidenceExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        ids = [r.id for r in results]
        assert len(set(ids)) == 3

    async def test_optional_fields_default_to_none(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        raw_evidence = [{"text": "Some evidence", "type": "citation"}]
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response(raw_evidence)
        )

        extractor = EvidenceExtractor(mock_anthropic_client)
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results[0].source_bookmark_id is None
        assert results[0].position_id is None

    async def test_appends_existing_positions_to_prompt(
        self,
        mock_anthropic_client: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_positions=[
                PositionRef(id="pos-001", text="AI improves consulting efficiency"),
            ],
        )
        mock_anthropic_client.messages.create = AsyncMock(
            return_value=_make_tool_response([])
        )

        extractor = EvidenceExtractor(mock_anthropic_client)
        await extractor.extract(sample_transcript, context)

        call_args = mock_anthropic_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "pos-001" in prompt
        assert "AI improves consulting efficiency" in prompt
