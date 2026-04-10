from __future__ import annotations

from sync.bookmark_transformer import BookmarkTransformer


def _make_notion_page(
    *,
    page_id: str = "page-001",
    title: str = "AI Agents in Consulting",
    url: str | None = "https://example.com/article",
    source: str | None = "Blog",
    summary: str = "A summary of the article.",
    viewpoint: str = "We agree with the core thesis.",
    theme: str | None = "Agentic AI",
    topics: list[str] | None = None,
    arc_buckets: list[str] | None = None,
    edge_or_foundational: str | None = "Edge",
    focus: str | None = "Technical",
    time_consumption: str | None = "Quick read",
    date_added: str | None = "2026-03-15",
    relation_theme_ids: list[str] | None = None,
    relation_topic_ids: list[str] | None = None,
    last_edited_time: str = "2026-04-01T12:00:00.000Z",
) -> dict:
    topics = topics or ["AI Agents", "Due Diligence"]
    if arc_buckets is None:
        arc_buckets = ["Agentic AI"]
    properties: dict = {
        "Name": {
            "type": "title",
            "title": [{"plain_text": title}],
        },
        "URL": {"type": "url", "url": url},
        "Source": {
            "type": "select",
            "select": {"name": source} if source else None,
        },
        "Summary": {
            "type": "rich_text",
            "rich_text": [{"plain_text": summary}] if summary else [],
        },
        "Valliance Viewpoint": {
            "type": "rich_text",
            "rich_text": [{"plain_text": viewpoint}] if viewpoint else [],
        },
        "* Theme": {
            "type": "select",
            "select": {"name": theme} if theme else None,
        },
        "Topics": {
            "type": "multi_select",
            "multi_select": [{"name": t} for t in topics],
        },
        "Edge or Foundational": {
            "type": "select",
            "select": {"name": edge_or_foundational} if edge_or_foundational else None,
        },
        "Focus": {
            "type": "select",
            "select": {"name": focus} if focus else None,
        },
        "Time Consumption": {
            "type": "select",
            "select": {"name": time_consumption} if time_consumption else None,
        },
        "Date Added": {
            "type": "date",
            "date": {"start": date_added} if date_added else None,
        },
        "Arc Bucket": {
            "type": "multi_select",
            "multi_select": [{"name": a} for a in arc_buckets],
        },
        "Valliance Themes": {
            "type": "relation",
            "relation": [{"id": pid} for pid in (relation_theme_ids or [])],
        },
        "Valliance Topics": {
            "type": "relation",
            "relation": [{"id": pid} for pid in (relation_topic_ids or [])],
        },
    }

    return {
        "id": page_id,
        "properties": properties,
        "last_edited_time": last_edited_time,
    }


class TestBookmarkTransformer:
    def test_transforms_full_page(self) -> None:
        page = _make_notion_page()
        result = BookmarkTransformer().transform(page)

        assert result["notion_id"] == "page-001"
        assert result["title"] == "AI Agents in Consulting"
        assert result["url"] == "https://example.com/article"
        assert result["source"] == "Blog"
        assert result["ai_summary"] == "A summary of the article."
        assert result["valliance_viewpoint"] == "We agree with the core thesis."
        assert result["theme_name"] == "Agentic AI"
        assert result["topic_names"] == ["AI Agents", "Due Diligence"]
        assert result["arc_bucket_names"] == ["Agentic AI"]
        assert result["edge_or_foundational"] == "Edge"
        assert result["focus"] == "Technical"
        assert result["time_consumption"] == "Quick read"
        assert result["date_added"] == "2026-03-15"
        assert result["last_edited_time"] == "2026-04-01T12:00:00.000Z"

    def test_handles_missing_optional_properties(self) -> None:
        page = _make_notion_page(
            url=None,
            source=None,
            theme=None,
            edge_or_foundational=None,
            focus=None,
            time_consumption=None,
            date_added=None,
        )
        result = BookmarkTransformer().transform(page)

        assert result["url"] is None
        assert result["source"] is None
        assert result["theme_name"] is None
        assert result["edge_or_foundational"] is None
        assert result["focus"] is None
        assert result["time_consumption"] is None
        assert result["date_added"] is None

    def test_deduplicates_topics_case_insensitively(self) -> None:
        page = _make_notion_page(topics=["AI Agents", "ai agents", "AI agents", "Due Diligence"])
        result = BookmarkTransformer().transform(page)

        assert result["topic_names"] == ["AI Agents", "Due Diligence"]

    def test_extracts_relation_ids(self) -> None:
        page = _make_notion_page(
            relation_theme_ids=["theme-page-1"],
            relation_topic_ids=["topic-page-1", "topic-page-2"],
        )
        result = BookmarkTransformer().transform(page)

        assert result["theme_page_ids"] == ["theme-page-1"]
        assert result["topic_page_ids"] == ["topic-page-1", "topic-page-2"]

    def test_empty_title_returns_empty_string(self) -> None:
        page = _make_notion_page()
        page["properties"]["Name"] = {"type": "title", "title": []}
        result = BookmarkTransformer().transform(page)

        assert result["title"] == ""

    def test_empty_rich_text_returns_empty_string(self) -> None:
        page = _make_notion_page(summary="", viewpoint="")
        page["properties"]["Summary"] = {"type": "rich_text", "rich_text": []}
        result = BookmarkTransformer().transform(page)

        assert result["ai_summary"] == ""

    def test_multi_part_title_concatenated(self) -> None:
        page = _make_notion_page()
        page["properties"]["Name"] = {
            "type": "title",
            "title": [{"plain_text": "Part 1 "}, {"plain_text": "Part 2"}],
        }
        result = BookmarkTransformer().transform(page)

        assert result["title"] == "Part 1 Part 2"

    def test_extracts_names_from_rollup_type(self) -> None:
        page = _make_notion_page(topics=[])
        page["properties"]["Topics"] = {
            "type": "rollup",
            "rollup": {
                "array": [
                    {"type": "title", "title": [{"plain_text": "Rolled Up Topic"}]},
                    {"type": "rich_text", "rich_text": [{"plain_text": "Another Topic"}]},
                ],
            },
        }
        result = BookmarkTransformer().transform(page)

        assert "Rolled Up Topic" in result["topic_names"]
        assert "Another Topic" in result["topic_names"]

    def test_relation_ids_empty_when_not_relation_type(self) -> None:
        page = _make_notion_page()
        page["properties"]["Valliance Themes"] = {
            "type": "rich_text",
            "rich_text": [],
        }
        result = BookmarkTransformer().transform(page)

        assert result["theme_page_ids"] == []

    def test_extracts_multiple_arc_buckets(self) -> None:
        page = _make_notion_page(arc_buckets=["Agentic AI", "Consulting Craft"])
        result = BookmarkTransformer().transform(page)

        assert result["arc_bucket_names"] == ["Agentic AI", "Consulting Craft"]

    def test_empty_arc_buckets(self) -> None:
        page = _make_notion_page(arc_buckets=[])
        result = BookmarkTransformer().transform(page)

        assert result["arc_bucket_names"] == []

    def test_handles_completely_empty_properties(self) -> None:
        page = {"id": "empty-page", "properties": {}, "last_edited_time": "2026-04-01T00:00:00Z"}
        result = BookmarkTransformer().transform(page)

        assert result["notion_id"] == "empty-page"
        assert result["title"] == ""
        assert result["topic_names"] == []
        assert result["arc_bucket_names"] == []
        assert result["theme_name"] is None
