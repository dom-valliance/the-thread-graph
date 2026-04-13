from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from extractors.evidence_extractor import EvidenceExtractor
from models.extraction import ExtractionContext, ExtractedEvidence, PositionRef


@pytest.fixture()
def extraction_context() -> ExtractionContext:
    return ExtractionContext(
        session_id="test-session-001",
        arc_name="AI Agents in Consulting",
    )


class TestEvidenceExtractor:
    @patch("extractors.evidence_extractor.evidence_graph")
    async def test_returns_valid_extracted_evidence(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedEvidence(
                id="ev-1",
                text="400 documents processed in 2 hours vs 3-4 days manually",
                type="data_point",
                position_id="pos-001",
            ),
            ExtractedEvidence(
                id="ev-2",
                text="94% accuracy rate on document review",
                type="data_point",
            ),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = EvidenceExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert len(results) == 2
        assert all(isinstance(r, ExtractedEvidence) for r in results)
        assert results[0].text == "400 documents processed in 2 hours vs 3-4 days manually"
        assert results[0].type == "data_point"
        assert results[0].position_id == "pos-001"
        assert results[1].position_id is None
        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["transcript"] == sample_transcript
        assert call_args["context"] == extraction_context

    @patch("extractors.evidence_extractor.evidence_graph")
    async def test_returns_empty_list_when_no_results(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = EvidenceExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results == []

    @patch("extractors.evidence_extractor.evidence_graph")
    async def test_each_item_gets_unique_id(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [
            ExtractedEvidence(id="ev-1", text="First evidence", type="citation"),
            ExtractedEvidence(id="ev-2", text="Second evidence", type="anecdote"),
            ExtractedEvidence(id="ev-3", text="Third evidence", type="case_study"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = EvidenceExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        ids = [r.id for r in results]
        assert len(set(ids)) == 3

    @patch("extractors.evidence_extractor.evidence_graph")
    async def test_optional_fields_default_to_none(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
        extraction_context: ExtractionContext,
    ) -> None:
        expected = [ExtractedEvidence(id="ev-1", text="Some evidence", type="citation")]
        mock_graph.ainvoke = AsyncMock(return_value={"results": expected})

        extractor = EvidenceExtractor()
        results = await extractor.extract(sample_transcript, extraction_context)

        assert results[0].source_bookmark_id is None
        assert results[0].position_id is None

    @patch("extractors.evidence_extractor.evidence_graph")
    async def test_passes_existing_positions_in_context(
        self,
        mock_graph: AsyncMock,
        sample_transcript: str,
    ) -> None:
        context = ExtractionContext(
            session_id="test-session-001",
            arc_name="Test Arc",
            existing_positions=[
                PositionRef(id="pos-001", text="AI improves consulting efficiency"),
            ],
        )
        mock_graph.ainvoke = AsyncMock(return_value={"results": []})

        extractor = EvidenceExtractor()
        await extractor.extract(sample_transcript, context)

        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args["context"] == context
        assert call_args["context"].existing_positions[0].id == "pos-001"
        assert call_args["context"].existing_positions[0].text == "AI improves consulting efficiency"
