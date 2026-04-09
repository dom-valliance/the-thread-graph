from __future__ import annotations


class SessionTransformer:
    """Transforms a Notion page from the Sessions database into an API-compatible dict."""

    def transform(self, notion_page: dict[str, object]) -> dict[str, object]:
        properties = notion_page.get("properties", {})
        return {
            "notion_id": notion_page["id"],
            "title": self._extract_title(properties.get("Name", {})),
            "transcript": self._extract_rich_text(properties.get("Transcript", {})),
            "summary": self._extract_rich_text(properties.get("Summary", {})),
            "date": self._extract_date(properties.get("Date", {})),
            "duration": self._extract_number(properties.get("Duration", {})),
            "theme_page_ids": self._extract_relation_ids(
                properties.get("Valliance Theme", {})
            ),
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

    def _extract_select(self, prop: dict[str, object]) -> str | None:
        select = prop.get("select")
        if select is None:
            return None
        return select.get("name")

    def _extract_date(self, prop: dict[str, object]) -> str | None:
        date = prop.get("date")
        if date is None:
            return None
        return date.get("start")

    def _extract_number(self, prop: dict[str, object]) -> int | None:
        value = prop.get("number")
        if value is None:
            return None
        return int(value)

    def _extract_relation_ids(self, prop: dict[str, object]) -> list[str]:
        """Extract page IDs from a Notion relation property."""
        if prop.get("type") != "relation":
            return []
        return [item["id"] for item in prop.get("relation", []) if "id" in item]
