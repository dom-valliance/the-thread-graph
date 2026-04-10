from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from sync.bookmark_transformer import BookmarkTransformer
from sync.session_transformer import SessionTransformer
from sync.sync_state import SyncState


# Import the module-level functions.  The runner imports dotenv at module
# level; it is safe because conftest.py adds the NLP root to sys.path.
from sync.runner import _resolve_relations, _get_known_themes, sync_database


class TestResolveRelations:
    async def test_merges_theme_from_relation_when_select_missing(self) -> None:
        batch = [
            {
                "title": "Article",
                "theme_name": None,
                "theme_page_ids": ["theme-page-1"],
                "topic_names": [],
                "topic_page_ids": [],
            },
        ]
        mock_client = AsyncMock()
        mock_client.resolve_page_titles = AsyncMock(
            return_value={"theme-page-1": "Agentic AI"}
        )

        await _resolve_relations(batch, mock_client)

        assert batch[0]["theme_name"] == "Agentic AI"
        assert "theme_page_ids" not in batch[0]

    async def test_preserves_select_theme_over_relation(self) -> None:
        batch = [
            {
                "title": "Article",
                "theme_name": "Original Theme",
                "theme_page_ids": ["theme-page-1"],
                "topic_names": [],
                "topic_page_ids": [],
            },
        ]
        mock_client = AsyncMock()
        mock_client.resolve_page_titles = AsyncMock(
            return_value={"theme-page-1": "Relation Theme"}
        )

        await _resolve_relations(batch, mock_client)

        assert batch[0]["theme_name"] == "Original Theme"

    async def test_merges_topics_from_relation_without_duplicates(self) -> None:
        batch = [
            {
                "title": "Article",
                "theme_name": None,
                "theme_page_ids": [],
                "topic_names": ["AI Agents"],
                "topic_page_ids": ["topic-page-1", "topic-page-2"],
            },
        ]
        mock_client = AsyncMock()
        mock_client.resolve_page_titles = AsyncMock(
            return_value={
                "topic-page-1": "AI Agents",
                "topic-page-2": "Due Diligence",
            }
        )

        await _resolve_relations(batch, mock_client)

        assert "AI Agents" in batch[0]["topic_names"]
        assert "Due Diligence" in batch[0]["topic_names"]
        assert batch[0]["topic_names"].count("AI Agents") == 1

    async def test_deduplicates_topics_case_insensitively(self) -> None:
        batch = [
            {
                "title": "Article",
                "theme_name": None,
                "theme_page_ids": [],
                "topic_names": ["ai agents"],
                "topic_page_ids": ["topic-page-1"],
            },
        ]
        mock_client = AsyncMock()
        mock_client.resolve_page_titles = AsyncMock(
            return_value={"topic-page-1": "AI Agents"}
        )

        await _resolve_relations(batch, mock_client)

        assert len(batch[0]["topic_names"]) == 1

    async def test_no_api_call_when_no_page_ids(self) -> None:
        batch = [
            {
                "title": "Article",
                "theme_name": "Theme",
                "theme_page_ids": [],
                "topic_names": ["Topic"],
                "topic_page_ids": [],
            },
        ]
        mock_client = AsyncMock()

        await _resolve_relations(batch, mock_client)

        mock_client.resolve_page_titles.assert_not_awaited()


class TestGetKnownThemes:
    async def test_extracts_themes_from_topics_response(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"name": "AI", "theme_name": "Agentic AI"},
                {"name": "Consulting", "theme_name": "Consulting Craft"},
                {"name": "Data", "theme_name": "Agentic AI"},
                {"name": "Misc", "theme_name": None},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await _get_known_themes(mock_client)

        assert result == ["Agentic AI", "Consulting Craft"]

    async def test_returns_empty_list_on_error(self) -> None:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.HTTPError("connection failed"))

        result = await _get_known_themes(mock_client)

        assert result == []


class TestSyncDatabase:
    async def test_syncs_single_page_batch(self, tmp_path: Path) -> None:
        notion_client = AsyncMock()
        notion_client.resolve_page_titles = AsyncMock(return_value={})
        notion_client.query_database = AsyncMock(
            return_value={
                "results": [
                    {
                        "id": "page-1",
                        "properties": {
                            "Name": {"type": "title", "title": [{"plain_text": "Test Bookmark"}]},
                        },
                        "last_edited_time": "2026-04-01T12:00:00.000Z",
                    },
                ],
                "has_more": False,
            }
        )

        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        api_client = AsyncMock()
        api_client.post = AsyncMock(return_value=mock_response)

        state = SyncState(tmp_path / "state.json")

        await sync_database(
            notion_client=notion_client,
            api_client=api_client,
            db_id="db-123",
            transformer=BookmarkTransformer(),
            endpoint="/sync/bookmarks",
            state=state,
            dry_run=False,
        )

        api_client.post.assert_awaited_once()
        assert state.get_last_sync("db-123") == "2026-04-01T12:00:00.000Z"

    async def test_dry_run_does_not_submit(self, tmp_path: Path) -> None:
        notion_client = AsyncMock()
        notion_client.resolve_page_titles = AsyncMock(return_value={})
        notion_client.query_database = AsyncMock(
            return_value={
                "results": [
                    {
                        "id": "page-1",
                        "properties": {
                            "Name": {"type": "title", "title": [{"plain_text": "Test"}]},
                        },
                        "last_edited_time": "2026-04-01T12:00:00.000Z",
                    },
                ],
                "has_more": False,
            }
        )

        api_client = AsyncMock()
        state = SyncState(tmp_path / "state.json")

        await sync_database(
            notion_client=notion_client,
            api_client=api_client,
            db_id="db-123",
            transformer=BookmarkTransformer(),
            endpoint="/sync/bookmarks",
            state=state,
            dry_run=True,
        )

        api_client.post.assert_not_awaited()
        assert state.get_last_sync("db-123") is None

    async def test_paginates_through_multiple_pages(self, tmp_path: Path) -> None:
        notion_client = AsyncMock()
        notion_client.resolve_page_titles = AsyncMock(return_value={})

        page_1_response = {
            "results": [
                {
                    "id": "page-1",
                    "properties": {"Name": {"type": "title", "title": [{"plain_text": "First"}]}},
                    "last_edited_time": "2026-04-01T10:00:00.000Z",
                },
            ],
            "has_more": True,
            "next_cursor": "cursor-abc",
        }
        page_2_response = {
            "results": [
                {
                    "id": "page-2",
                    "properties": {"Name": {"type": "title", "title": [{"plain_text": "Second"}]}},
                    "last_edited_time": "2026-04-01T12:00:00.000Z",
                },
            ],
            "has_more": False,
        }
        notion_client.query_database = AsyncMock(
            side_effect=[page_1_response, page_2_response]
        )

        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        api_client = AsyncMock()
        api_client.post = AsyncMock(return_value=mock_response)

        state = SyncState(tmp_path / "state.json")

        await sync_database(
            notion_client=notion_client,
            api_client=api_client,
            db_id="db-123",
            transformer=BookmarkTransformer(),
            endpoint="/sync/bookmarks",
            state=state,
            dry_run=False,
        )

        assert api_client.post.await_count == 2
        assert state.get_last_sync("db-123") == "2026-04-01T12:00:00.000Z"

    async def test_applies_enrich_callback(self, tmp_path: Path) -> None:
        notion_client = AsyncMock()
        notion_client.resolve_page_titles = AsyncMock(return_value={})
        notion_client.query_database = AsyncMock(
            return_value={
                "results": [
                    {
                        "id": "page-1",
                        "properties": {"Name": {"type": "title", "title": [{"plain_text": "Test"}]}},
                        "last_edited_time": "2026-04-01T12:00:00.000Z",
                    },
                ],
                "has_more": False,
            }
        )

        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        api_client = AsyncMock()
        api_client.post = AsyncMock(return_value=mock_response)

        state = SyncState(tmp_path / "state.json")

        async def enrich(batch):
            for item in batch:
                item["theme_name"] = "Enriched Theme"
            return batch

        await sync_database(
            notion_client=notion_client,
            api_client=api_client,
            db_id="db-123",
            transformer=BookmarkTransformer(),
            endpoint="/sync/bookmarks",
            state=state,
            dry_run=False,
            enrich=enrich,
        )

        submitted = api_client.post.call_args[1]["json"]
        assert submitted[0]["theme_name"] == "Enriched Theme"

    async def test_uses_incremental_filter_when_last_sync_exists(
        self, tmp_path: Path,
    ) -> None:
        notion_client = AsyncMock()
        notion_client.resolve_page_titles = AsyncMock(return_value={})
        notion_client.query_database = AsyncMock(
            return_value={"results": [], "has_more": False}
        )

        api_client = AsyncMock()
        state = SyncState(tmp_path / "state.json")
        state.update_last_sync("db-123", "2026-03-01T00:00:00Z")

        await sync_database(
            notion_client=notion_client,
            api_client=api_client,
            db_id="db-123",
            transformer=BookmarkTransformer(),
            endpoint="/sync/bookmarks",
            state=state,
            dry_run=False,
        )

        call_args = notion_client.query_database.call_args
        assert call_args.kwargs.get("filter") is not None or call_args[1].get("filter") is not None
