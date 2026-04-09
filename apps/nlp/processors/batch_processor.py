from __future__ import annotations

import logging

from client.api_client import ApiClient
from models.session import SessionInput
from processors.transcript_processor import TranscriptProcessor

logger = logging.getLogger(__name__)

MAX_SESSIONS_PER_RUN = 5


class BatchProcessor:
    def __init__(
        self,
        transcript_processor: TranscriptProcessor,
        api_client: ApiClient,
    ) -> None:
        self._transcript_processor = transcript_processor
        self._api_client = api_client

    async def process_batch(self, max_sessions: int = MAX_SESSIONS_PER_RUN) -> None:
        sessions = await self._api_client.get_unprocessed_sessions()
        sessions_to_process = sessions[:max_sessions]

        if not sessions_to_process:
            logger.info("No unprocessed sessions found.")
            return

        logger.info("Processing %d session(s).", len(sessions_to_process))

        for session in sessions_to_process:
            await self._process_single(session)

    async def _process_single(self, session: SessionInput) -> None:
        logger.info("Processing session: %s (%s)", session.title, session.notion_id)

        try:
            context = await self._api_client.get_extraction_context(session.notion_id)
            result = await self._transcript_processor.process(session, context)

            if result.arguments:
                await self._api_client.submit_arguments(
                    [arg.model_dump() for arg in result.arguments]
                )
                logger.info("Submitted %d argument(s).", len(result.arguments))

            if result.action_items:
                await self._api_client.submit_action_items(
                    [item.model_dump() for item in result.action_items]
                )
                logger.info("Submitted %d action item(s).", len(result.action_items))

            if result.evidence:
                await self._api_client.submit_evidence(
                    [ev.model_dump() for ev in result.evidence]
                )
                logger.info("Submitted %d evidence item(s).", len(result.evidence))

            await self._api_client.mark_session_enriched(session.notion_id)
            logger.info("Marked session %s as enriched.", session.notion_id)

        except Exception:
            logger.exception(
                "Failed to process session %s (%s).", session.title, session.notion_id
            )
