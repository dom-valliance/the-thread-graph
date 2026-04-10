from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from sync.notion_client import RateLimitedNotionClient, RateLimiter


class TestExtractPageTitle:
    def test_extracts_title_from_properties(self) -> None:
        page = {
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "My Page Title"}],
                },
            },
        }
        assert RateLimitedNotionClient._extract_page_title(page) == "My Page Title"

    def test_concatenates_multiple_title_parts(self) -> None:
        page = {
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "Part 1 "}, {"plain_text": "Part 2"}],
                },
            },
        }
        assert RateLimitedNotionClient._extract_page_title(page) == "Part 1 Part 2"

    def test_returns_empty_string_when_no_title_property(self) -> None:
        page = {
            "properties": {
                "Other": {"type": "rich_text", "rich_text": []},
            },
        }
        assert RateLimitedNotionClient._extract_page_title(page) == ""

    def test_returns_empty_string_when_title_items_empty(self) -> None:
        page = {
            "properties": {
                "Name": {"type": "title", "title": []},
            },
        }
        assert RateLimitedNotionClient._extract_page_title(page) == ""

    def test_returns_empty_string_when_no_properties(self) -> None:
        page: dict = {}
        assert RateLimitedNotionClient._extract_page_title(page) == ""


class TestResolvePageTitles:
    async def test_resolves_page_ids_to_titles(self) -> None:
        client = RateLimitedNotionClient("fake-key")

        async def mock_get_page(page_id: str) -> dict:
            return {
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": f"Title for {page_id}"}]},
                },
            }

        client.get_page = mock_get_page

        result = await client.resolve_page_titles(["page-1", "page-2"])

        assert result == {
            "page-1": "Title for page-1",
            "page-2": "Title for page-2",
        }
        await client.close()

    async def test_caches_resolved_titles(self) -> None:
        client = RateLimitedNotionClient("fake-key")
        call_count = 0

        async def mock_get_page(page_id: str) -> dict:
            nonlocal call_count
            call_count += 1
            return {
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "Cached Title"}]},
                },
            }

        client.get_page = mock_get_page

        await client.resolve_page_titles(["page-1"])
        await client.resolve_page_titles(["page-1"])

        assert call_count == 1
        await client.close()

    async def test_skips_failed_pages(self) -> None:
        client = RateLimitedNotionClient("fake-key")

        async def mock_get_page(page_id: str) -> dict:
            if page_id == "bad-page":
                raise RuntimeError("Not found")
            return {
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "Good Title"}]},
                },
            }

        client.get_page = mock_get_page

        result = await client.resolve_page_titles(["good-page", "bad-page"])

        assert "good-page" in result
        assert "bad-page" not in result
        await client.close()


class TestQueryDatabase:
    async def test_passes_filter_and_cursor(self) -> None:
        client = RateLimitedNotionClient("fake-key")
        expected_response = {"results": [], "has_more": False}

        async def mock_request(method, path, json=None):
            return httpx.Response(
                200,
                json=expected_response,
                request=httpx.Request(method, f"https://api.notion.com/v1{path}"),
            )

        client._http.request = mock_request
        client._rate_limiter.acquire = AsyncMock()

        result = await client.query_database(
            "db-123",
            filter={"timestamp": "last_edited_time"},
            start_cursor="cursor-abc",
        )

        assert result == expected_response
        await client.close()


class TestRequestWithRetry:
    async def test_retries_on_429(self) -> None:
        client = RateLimitedNotionClient("fake-key")
        client._rate_limiter.acquire = AsyncMock()

        call_count = 0

        async def mock_request(method, path, json=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    429,
                    headers={"Retry-After": "0.01"},
                    request=httpx.Request(method, f"https://api.notion.com/v1{path}"),
                )
            return httpx.Response(
                200,
                json={"ok": True},
                request=httpx.Request(method, f"https://api.notion.com/v1{path}"),
            )

        client._http.request = mock_request

        result = await client._request_with_retry("GET", "/pages/123")

        assert result == {"ok": True}
        assert call_count == 2
        await client.close()

    async def test_retries_on_5xx(self) -> None:
        client = RateLimitedNotionClient("fake-key")
        client._rate_limiter.acquire = AsyncMock()

        call_count = 0

        async def mock_request(method, path, json=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    500,
                    json={"error": "internal"},
                    request=httpx.Request(method, f"https://api.notion.com/v1{path}"),
                )
            return httpx.Response(
                200,
                json={"ok": True},
                request=httpx.Request(method, f"https://api.notion.com/v1{path}"),
            )

        client._http.request = mock_request

        result = await client._request_with_retry("GET", "/pages/123")

        assert result == {"ok": True}
        assert call_count == 2
        await client.close()

    async def test_raises_on_4xx_without_retry(self) -> None:
        client = RateLimitedNotionClient("fake-key")
        client._rate_limiter.acquire = AsyncMock()

        async def mock_request(method, path, json=None):
            return httpx.Response(
                404,
                json={"error": "not found"},
                request=httpx.Request(method, f"https://api.notion.com/v1{path}"),
            )

        client._http.request = mock_request

        with pytest.raises(httpx.HTTPStatusError):
            await client._request_with_retry("GET", "/pages/nonexistent")

        await client.close()


class TestRateLimiter:
    async def test_acquire_does_not_block_on_first_call(self) -> None:
        limiter = RateLimiter(requests_per_second=3)
        await limiter.acquire()
