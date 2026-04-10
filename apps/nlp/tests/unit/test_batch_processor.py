from __future__ import annotations

from unittest.mock import AsyncMock, call

import pytest

from models.extraction import (
    ExtractionContext,
    ExtractionResult,
    ExtractedArgument,
    ExtractedActionItem,
    ExtractedEvidence,
)
from models.session import SessionInput
from processors.batch_processor import BatchProcessor


@pytest.fixture()
def mock_api_client() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def mock_transcript_processor() -> AsyncMock:
    return AsyncMock()


def _make_session(notion_id: str, title: str) -> SessionInput:
    return SessionInput(
        notion_id=notion_id,
        title=title,
        transcript="Some transcript content.",
    )


def _make_result(
    *,
    arguments: int = 0,
    action_items: int = 0,
    evidence: int = 0,
) -> ExtractionResult:
    return ExtractionResult(
        arguments=[
            ExtractedArgument(
                id=f"arg-{i}", text=f"Argument {i}",
                sentiment="supports", relationship_type="SUPPORTS",
            )
            for i in range(arguments)
        ],
        action_items=[
            ExtractedActionItem(id=f"ai-{i}", text=f"Action {i}")
            for i in range(action_items)
        ],
        evidence=[
            ExtractedEvidence(id=f"ev-{i}", text=f"Evidence {i}", type="data_point")
            for i in range(evidence)
        ],
    )


class TestBatchProcessor:
    async def test_processes_up_to_max_sessions(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [_make_session(f"s-{i}", f"Session {i}") for i in range(10)]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            return_value=ExtractionContext(session_id="s-0")
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result()
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch(max_sessions=3)

        assert mock_transcript_processor.process.await_count == 3

    async def test_skips_when_no_unprocessed_sessions(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=[])

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_transcript_processor.process.assert_not_awaited()

    async def test_submits_arguments_to_api(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [_make_session("s-1", "Session 1")]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            return_value=ExtractionContext(session_id="s-1")
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result(arguments=2)
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_api_client.submit_arguments.assert_awaited_once()
        submitted = mock_api_client.submit_arguments.call_args[0][0]
        assert len(submitted) == 2

    async def test_submits_action_items_to_api(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [_make_session("s-1", "Session 1")]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            return_value=ExtractionContext(session_id="s-1")
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result(action_items=3)
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_api_client.submit_action_items.assert_awaited_once()
        submitted = mock_api_client.submit_action_items.call_args[0][0]
        assert len(submitted) == 3

    async def test_submits_evidence_to_api(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [_make_session("s-1", "Session 1")]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            return_value=ExtractionContext(session_id="s-1")
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result(evidence=1)
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_api_client.submit_evidence.assert_awaited_once()

    async def test_marks_session_enriched_after_processing(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [_make_session("s-1", "Session 1")]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            return_value=ExtractionContext(session_id="s-1")
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result(arguments=1)
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_api_client.mark_session_enriched.assert_awaited_once_with("s-1")

    async def test_skips_empty_result_types(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [_make_session("s-1", "Session 1")]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            return_value=ExtractionContext(session_id="s-1")
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result()
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_api_client.submit_arguments.assert_not_awaited()
        mock_api_client.submit_action_items.assert_not_awaited()
        mock_api_client.submit_evidence.assert_not_awaited()
        mock_api_client.mark_session_enriched.assert_awaited_once()

    async def test_continues_processing_when_one_session_fails(
        self,
        mock_api_client: AsyncMock,
        mock_transcript_processor: AsyncMock,
    ) -> None:
        sessions = [
            _make_session("s-1", "Session 1"),
            _make_session("s-2", "Session 2"),
        ]
        mock_api_client.get_unprocessed_sessions = AsyncMock(return_value=sessions)
        mock_api_client.get_extraction_context = AsyncMock(
            side_effect=[
                RuntimeError("API down"),
                ExtractionContext(session_id="s-2"),
            ]
        )
        mock_transcript_processor.process = AsyncMock(
            return_value=_make_result(arguments=1)
        )

        processor = BatchProcessor(mock_transcript_processor, mock_api_client)
        await processor.process_batch()

        mock_api_client.mark_session_enriched.assert_awaited_once_with("s-2")
