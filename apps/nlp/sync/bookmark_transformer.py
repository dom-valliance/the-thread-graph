from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Maps Notion arc tag variants to the canonical Arc name in Neo4j.
# Keep keys lowercase and stripped; lookups normalise the same way.
ARC_NAME_ALIASES: dict[str, str] = {
    "agentic ai": "Agentic AI",
    "palantir/ontology": "Palantir / Ontology",
    "palantir / ontology": "Palantir / Ontology",
    "palantir": "Palantir / Ontology",
    "ontology": "Palantir / Ontology",
    "people enablement": "People Enablement",
    "consulting craft": "The Consulting Craft",
    "the consulting craft": "The Consulting Craft",
    "agentic engineering": "Agentic Engineering",
    "value realisation": "Value Realisation",
    "value realization": "Value Realisation",
}


def normalise_arc_name(name: str) -> str | None:
    if not name:
        return None
    return ARC_NAME_ALIASES.get(name.strip().lower(), name.strip())


class BookmarkTransformer:
    """Transforms a Notion page from the Bookmarks database into an API-compatible dict."""

    def transform(self, notion_page: dict[str, object]) -> dict[str, object]:
        properties = notion_page.get("properties", {})

        # "* Theme" (select) is gospel when present.
        # "Valliance Themes" is a relation (page IDs resolved by the runner).
        # "Topics" (multi_select) feeds into topic_names.
        # "Valliance Topics" is a relation (page IDs resolved by the runner).
        theme = self._extract_select(properties.get("* Theme", {}))
        raw_topics = self._extract_names(properties.get("Topics", {}))

        # Deduplicate topics, preserving order.
        seen: set[str] = set()
        topic_names: list[str] = []
        for name in raw_topics:
            lower = name.lower()
            if lower not in seen:
                seen.add(lower)
                topic_names.append(name)

        return {
            "notion_id": notion_page["id"],
            "title": self._extract_title(properties.get("Name", {})),
            "url": self._extract_url(properties.get("URL", {})),
            "source": self._extract_select(properties.get("Source", {})),
            "ai_summary": self._extract_rich_text(properties.get("Summary", {})),
            "valliance_viewpoint": self._extract_rich_text(
                properties.get("Valliance Viewpoint", {})
            ),
            "edge_or_foundational": self._extract_select(
                properties.get("Edge or Foundational", {})
            ),
            "focus": self._extract_select(properties.get("Focus", {})),
            "time_consumption": self._extract_select(
                properties.get("Time Consumption", {})
            ),
            "date_added": (
                self._extract_date(properties.get("Date Added", {}))
                or notion_page.get("created_time")
            ),
            "topic_names": topic_names,
            "theme_name": theme,
            "arc_bucket_names": [
                normalised
                for raw in self._extract_multi_select(properties.get("Arc Bucket", {}))
                if (normalised := normalise_arc_name(raw)) is not None
            ],
            "theme_page_ids": self._extract_relation_ids(
                properties.get("Valliance Themes", {})
            ),
            "topic_page_ids": self._extract_relation_ids(
                properties.get("Valliance Topics", {})
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

    def _extract_url(self, prop: dict[str, object]) -> str | None:
        return prop.get("url")

    def _extract_select(self, prop: dict[str, object]) -> str | None:
        select = prop.get("select")
        if select is None:
            return None
        return select.get("name")

    def _extract_multi_select(self, prop: dict[str, object]) -> list[str]:
        items = prop.get("multi_select", [])
        return [item.get("name", "") for item in items]

    def _extract_names(self, prop: dict[str, object]) -> list[str]:
        """Extract names from multi_select or rollup properties."""
        prop_type = prop.get("type")

        if prop_type == "multi_select":
            return [item.get("name", "") for item in prop.get("multi_select", [])]

        if prop_type == "rollup":
            rollup = prop.get("rollup", {})
            results = rollup.get("array", [])
            names: list[str] = []
            for item in results:
                item_type = item.get("type")
                if item_type == "title":
                    names.append(
                        "".join(t.get("plain_text", "") for t in item.get("title", []))
                    )
                elif item_type == "rich_text":
                    names.append(
                        "".join(t.get("plain_text", "") for t in item.get("rich_text", []))
                    )
            return [n for n in names if n]

        return []

    def _extract_date(self, prop: dict[str, object]) -> str | None:
        prop_type = prop.get("type")
        if prop_type == "date":
            date = prop.get("date")
            if date is None:
                return None
            return date.get("start")
        if prop_type in ("created_time", "last_edited_time"):
            value = prop.get(prop_type)
            return value if isinstance(value, str) else None
        # Fallback for cases where type is missing but date payload exists.
        date = prop.get("date")
        if isinstance(date, dict):
            return date.get("start")
        return None

    def _extract_relation_ids(self, prop: dict[str, object]) -> list[str]:
        """Extract page IDs from a Notion relation property."""
        if prop.get("type") != "relation":
            return []
        return [item["id"] for item in prop.get("relation", []) if "id" in item]
