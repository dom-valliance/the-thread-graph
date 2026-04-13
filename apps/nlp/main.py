from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from client.api_client import ApiClient
from extractors.argument_extractor import ArgumentExtractor
from extractors.action_item_extractor import ActionItemExtractor
from extractors.evidence_extractor import EvidenceExtractor
from extractors.entity_extractor import EntityExtractor
from processors.batch_processor import BatchProcessor
from processors.transcript_processor import TranscriptProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_processor() -> TranscriptProcessor:
    return TranscriptProcessor(
        argument_extractor=ArgumentExtractor(),
        action_item_extractor=ActionItemExtractor(),
        evidence_extractor=EvidenceExtractor(),
        entity_extractor=EntityExtractor(),
    )


async def run_single(session_id: str) -> None:
    api_client = ApiClient()
    processor = build_processor()

    try:
        sessions = await api_client.get_unprocessed_sessions()
        session = next(
            (s for s in sessions if s.notion_id == session_id),
            None,
        )
        if session is None:
            logger.error("Session %s not found or already enriched.", session_id)
            sys.exit(1)

        context = await api_client.get_extraction_context(session_id)
        result = await processor.process(session, context)

        if result.arguments:
            await api_client.submit_arguments(
                [arg.model_dump() for arg in result.arguments]
            )
        if result.action_items:
            await api_client.submit_action_items(
                [item.model_dump() for item in result.action_items]
            )
        if result.evidence:
            await api_client.submit_evidence(
                [ev.model_dump() for ev in result.evidence]
            )

        await api_client.mark_session_enriched(session_id)
        logger.info("Successfully enriched session %s.", session_id)
    finally:
        await api_client.close()


async def run_batch() -> None:
    api_client = ApiClient()
    processor = build_processor()
    batch = BatchProcessor(processor, api_client)

    try:
        await batch.process_batch()
    finally:
        await api_client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Valliance Graph NLP enrichment pipeline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--session-id",
        help="Process a single session by its Notion ID.",
    )
    group.add_argument(
        "--batch",
        action="store_true",
        help="Process all unprocessed sessions (up to 5).",
    )
    args = parser.parse_args()

    if args.session_id:
        asyncio.run(run_single(args.session_id))
    else:
        asyncio.run(run_batch())


if __name__ == "__main__":
    main()
