from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SessionTransformer:
    """Transforms a Notion page from the Discussion Recordings database into an API-compatible dict.

    Actual Notion properties:
        Name (title): recording title
        Date Created (date): when the discussion happened
        Bookmark (relation): links to the parent Bookmark page
        AI Suggested Viewpoint (rich_text): AI-generated viewpoint summary

    Note: the actual transcript lives in the page body (block children),
    not in a property. Fetching it requires the blocks API and is not
    yet implemented.
    """

    _logged_keys = False

    def transform(self, notion_page: dict[str, object]) -> dict[str, object]:
        properties = notion_page.get("properties", {})

        if not SessionTransformer._logged_keys:
            for name, prop in properties.items():
                logger.info(
                    "Session property: %s type=%s",
                    name,
                    prop.get("type") if isinstance(prop, dict) else "unknown",
                )
            SessionTransformer._logged_keys = True

        bookmark_ids = self._extract_relation_ids(properties.get("Bookmark", {}))

        return {
            "notion_id": notion_page["id"],
            "title": self._extract_title(properties.get("Name", {})),
            "date": self._extract_date(properties.get("Date Created", {})),
            "ai_suggested_viewpoint": self._extract_rich_text(
                properties.get("AI Suggested Viewpoint", {})
            ),
            "bookmark_notion_id": bookmark_ids[0] if bookmark_ids else None,
            "last_edited_time": notion_page.get("last_edited_time"),
        }

    def _extract_title(self, prop: dict[str, object]) -> str:
        title_items = prop.get("title", [])
        if not title_items:
            return ""
        return "".join(item.get("plain_text", "") for item in title_items)

    def _extract_rich_text(self, prop: dict[str, object]) -> str:
        text_items = prop.get("rich_text", [])
        if not text_items:
            return ""
        return "".join(item.get("plain_text", "") for item in text_items)

    def _extract_date(self, prop: dict[str, object]) -> str | None:
        date = prop.get("date")
        if date is None:
            return None
        return date.get("start")

    def _extract_relation_ids(self, prop: dict[str, object]) -> list[str]:
        """Extract page IDs from a Notion relation property."""
        if prop.get("type") != "relation":
            return []
        return [item["id"] for item in prop.get("relation", []) if "id" in item]
