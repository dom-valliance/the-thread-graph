from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from collections.abc import Callable, Awaitable

from dotenv import load_dotenv

load_dotenv()

import httpx

from sync.bookmark_transformer import BookmarkTransformer
from sync.notion_client import RateLimitedNotionClient
from sync.session_transformer import SessionTransformer
from sync.sync_state import SyncState
from sync.theme_classifier import ThemeClassifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SUBMIT_BATCH_SIZE = 10

BatchEnricher = Callable[[list[dict[str, object]]], Awaitable[list[dict[str, object]]]]


async def _resolve_relations(
    batch: list[dict[str, object]],
    notion_client: RateLimitedNotionClient,
) -> None:
    """Resolve relation page IDs to names in-place.

    Collects all unique page IDs from ``theme_page_ids`` and
    ``topic_page_ids`` fields, resolves them to titles via the Notion
    API, then merges the resolved names into ``theme_name`` and
    ``topic_names``.
    """
    all_page_ids: set[str] = set()
    for item in batch:
        all_page_ids.update(item.get("theme_page_ids", []))
        all_page_ids.update(item.get("topic_page_ids", []))

    if not all_page_ids:
        return

    title_map = await notion_client.resolve_page_titles(list(all_page_ids))

    for item in batch:
        # Resolve theme: relation-resolved name is used only when
        # there is no select-based theme_name already set.
        theme_ids = item.pop("theme_page_ids", [])
        if not item.get("theme_name") and theme_ids:
            resolved = [title_map[pid] for pid in theme_ids if pid in title_map]
            if resolved:
                item["theme_name"] = resolved[0]

        # Resolve topics: merge relation-resolved names into topic_names.
        topic_ids = item.pop("topic_page_ids", [])
        if topic_ids:
            existing = set(n.lower() for n in item.get("topic_names", []))
            for pid in topic_ids:
                name = title_map.get(pid)
                if name and name.lower() not in existing:
                    item.setdefault("topic_names", []).append(name)
                    existing.add(name.lower())


async def sync_database(
    notion_client: RateLimitedNotionClient,
    api_client: httpx.AsyncClient,
    db_id: str,
    transformer: BookmarkTransformer | SessionTransformer,
    endpoint: str,
    state: SyncState,
    dry_run: bool,
    enrich: BatchEnricher | None = None,
) -> None:
    last_sync = state.get_last_sync(db_id)

    notion_filter: dict[str, object] | None = None
    if last_sync is not None:
        notion_filter = {
            "timestamp": "last_edited_time",
            "last_edited_time": {"after": last_sync},
        }

    latest_timestamp: str | None = None
    cursor: str | None = None
    total_synced = 0

    while True:
        response = await notion_client.query_database(
            db_id, filter=notion_filter, start_cursor=cursor
        )
        results = response.get("results", [])

        if not results:
            break

        batch: list[dict[str, object]] = []
        for page in results:
            transformed = transformer.transform(page)
            batch.append(transformed)

            page_edited = page.get("last_edited_time", "")
            if latest_timestamp is None or page_edited > latest_timestamp:
                latest_timestamp = page_edited

        # Resolve relation page IDs to names.
        await _resolve_relations(batch, notion_client)

        if enrich is not None:
            batch = await enrich(batch)

        if dry_run:
            for item in batch:
                logger.info(
                    "[DRY RUN] Would sync: %s (theme: %s, topics: %s)",
                    item.get("title", item.get("notion_id")),
                    item.get("theme_name", "—"),
                    item.get("topic_names", []),
                )
        else:
            for i in range(0, len(batch), SUBMIT_BATCH_SIZE):
                chunk = batch[i : i + SUBMIT_BATCH_SIZE]
                resp = await api_client.post(endpoint, json=chunk)
                resp.raise_for_status()

        total_synced += len(batch)

        if not response.get("has_more", False):
            break
        cursor = response.get("next_cursor")

        # Pace requests when LLM enrichment is active to avoid 529 overload errors.
        if enrich is not None:
            await asyncio.sleep(1.0)

    if latest_timestamp is not None and not dry_run:
        state.update_last_sync(db_id, latest_timestamp)

    logger.info(
        "Synced %d record(s) from database %s.%s",
        total_synced,
        db_id,
        " (dry run)" if dry_run else "",
    )


async def _get_known_themes(api_client: httpx.AsyncClient) -> list[str]:
    """Fetch existing theme names from the API to guide classification."""
    try:
        resp = await api_client.get("/topics")
        resp.raise_for_status()
        data = resp.json().get("data", [])
        themes: set[str] = set()
        for topic in data:
            theme = topic.get("theme_name")
            if theme:
                themes.add(theme)
        return sorted(themes)
    except httpx.HTTPError:
        logger.debug("Could not fetch known themes; classifier will infer freely.")
        return []


async def run_sync(db_target: str, dry_run: bool, full: bool = False) -> None:
    notion_api_key = os.environ["NOTION_API_KEY"]
    api_base_url = os.environ["API_BASE_URL"].rstrip("/")
    bookmarks_db_id = os.environ.get("NOTION_BOOKMARKS_DB_ID", "")
    sessions_db_id = os.environ.get("NOTION_SESSIONS_DB_ID", "")

    notion_client = RateLimitedNotionClient(notion_api_key)
    api_client = httpx.AsyncClient(
        base_url=f"{api_base_url}/api/v1",
        timeout=120.0,
    )
    state = SyncState()

    if full:
        if db_target in ("bookmarks", "all") and bookmarks_db_id:
            state.clear(bookmarks_db_id)
            logger.info("Cleared sync state for bookmarks database.")
        if db_target in ("sessions", "all") and sessions_db_id:
            state.clear(sessions_db_id)
            logger.info("Cleared sync state for sessions database.")

    try:
        if db_target in ("bookmarks", "all"):
            if not bookmarks_db_id:
                logger.error("NOTION_BOOKMARKS_DB_ID is not set.")
                sys.exit(1)

            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
            enrich: BatchEnricher | None = None
            if anthropic_key:
                known_themes = await _get_known_themes(api_client)
                classifier = ThemeClassifier(known_themes=known_themes)
                enrich = classifier.classify_batch
                logger.info(
                    "Theme classification enabled (%d known themes).",
                    len(known_themes),
                )
            else:
                logger.warning(
                    "ANTHROPIC_API_KEY not set; theme classification disabled."
                )

            await sync_database(
                notion_client=notion_client,
                api_client=api_client,
                db_id=bookmarks_db_id,
                transformer=BookmarkTransformer(),
                endpoint="/sync/bookmarks",
                state=state,
                dry_run=dry_run,
                enrich=enrich,
            )

        if db_target in ("sessions", "all"):
            if not sessions_db_id:
                logger.error("NOTION_SESSIONS_DB_ID is not set.")
                sys.exit(1)
            await sync_database(
                notion_client=notion_client,
                api_client=api_client,
                db_id=sessions_db_id,
                transformer=SessionTransformer(),
                endpoint="/sync/sessions",
                state=state,
                dry_run=dry_run,
            )
    finally:
        await notion_client.close()
        await api_client.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Valliance Graph Notion sync service")
    parser.add_argument(
        "--db",
        choices=["bookmarks", "sessions", "all"],
        default="all",
        help="Which Notion database(s) to sync.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be synced without submitting to the API.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Ignore last sync timestamp and re-sync all records.",
    )
    args = parser.parse_args()

    asyncio.run(run_sync(args.db, args.dry_run, args.full))


if __name__ == "__main__":
    main()
