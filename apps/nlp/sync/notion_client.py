from __future__ import annotations

import asyncio
import logging
import time

import httpx

logger = logging.getLogger(__name__)

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"
MAX_RETRIES = 3
RATE_LIMIT_RPS = 3


class RateLimiter:
    """Token bucket rate limiter for Notion API (3 requests per second)."""

    def __init__(self, requests_per_second: float = RATE_LIMIT_RPS) -> None:
        self._interval = 1.0 / requests_per_second
        self._last_request_time = 0.0

    async def acquire(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._interval:
            await asyncio.sleep(self._interval - elapsed)
        self._last_request_time = time.monotonic()


class RateLimitedNotionClient:
    def __init__(self, api_key: str) -> None:
        self._http = httpx.AsyncClient(
            base_url=NOTION_BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        self._rate_limiter = RateLimiter()
        self._title_cache: dict[str, str] = {}

    async def close(self) -> None:
        await self._http.aclose()

    async def get_page(self, page_id: str) -> dict[str, object]:
        """Fetch a single Notion page by ID."""
        return await self._request_with_retry("GET", f"/pages/{page_id}")

    async def resolve_page_titles(
        self, page_ids: list[str]
    ) -> dict[str, str]:
        """Resolve a list of Notion page IDs to their title strings.

        Results are cached in-memory to avoid redundant API calls for
        pages that appear across multiple records.
        """
        result: dict[str, str] = {}
        to_fetch: list[str] = []

        for pid in page_ids:
            if pid in self._title_cache:
                result[pid] = self._title_cache[pid]
            else:
                to_fetch.append(pid)

        for pid in to_fetch:
            try:
                page = await self.get_page(pid)
                title = self._extract_page_title(page)
                self._title_cache[pid] = title
                result[pid] = title
            except (httpx.HTTPStatusError, RuntimeError):
                logger.warning("Failed to resolve page title for %s", pid)

        return result

    @staticmethod
    def _extract_page_title(page: dict[str, object]) -> str:
        """Extract the title from a Notion page's properties."""
        properties = page.get("properties", {})
        for prop in properties.values():
            if prop.get("type") == "title":
                title_items = prop.get("title", [])
                return "".join(
                    item.get("plain_text", "") for item in title_items
                )
        return ""

    async def query_database(
        self,
        db_id: str,
        filter: dict[str, object] | None = None,
        start_cursor: str | None = None,
    ) -> dict[str, object]:
        body: dict[str, object] = {}
        if filter is not None:
            body["filter"] = filter
        if start_cursor is not None:
            body["start_cursor"] = start_cursor

        return await self._request_with_retry(
            "POST", f"/databases/{db_id}/query", json=body
        )

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        json: dict[str, object] | None = None,
    ) -> dict[str, object]:
        backoff_seconds = 1.0

        for attempt in range(MAX_RETRIES + 1):
            await self._rate_limiter.acquire()

            try:
                response = await self._http.request(method, path, json=json)

                if response.status_code == 429:
                    retry_after = float(
                        response.headers.get("Retry-After", str(backoff_seconds))
                    )
                    if attempt < MAX_RETRIES:
                        logger.warning(
                            "Rate limited by Notion. Retrying in %.1fs (attempt %d/%d).",
                            retry_after,
                            attempt + 1,
                            MAX_RETRIES,
                        )
                        await asyncio.sleep(retry_after)
                        backoff_seconds *= 2
                        continue
                    response.raise_for_status()

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError:
                if attempt < MAX_RETRIES and response.status_code >= 500:
                    logger.warning(
                        "Notion API returned %d. Retrying in %.1fs (attempt %d/%d).",
                        response.status_code,
                        backoff_seconds,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    await asyncio.sleep(backoff_seconds)
                    backoff_seconds *= 2
                    continue
                raise

        msg = f"Notion API request failed after {MAX_RETRIES} retries: {method} {path}"
        raise RuntimeError(msg)
