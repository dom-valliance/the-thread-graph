from __future__ import annotations

from sync.session_transformer import SessionTransformer


def _make_notion_page(
    *,
    page_id: str = "session-001",
    title: str = "AI Policy Discussion",
    date: str | None = "2026-03-20",
    ai_viewpoint: str = "This discussion covers governance frameworks.",
    bookmark_ids: list[str] | None = None,
    last_edited_time: str = "2026-04-01T12:00:00.000Z",
) -> dict:
    properties: dict = {
        "Name": {
            "type": "title",
            "title": [{"plain_text": title}] if title else [],
        },
        "Date Created": {
            "type": "date",
            "date": {"start": date} if date else None,
        },
        "AI Suggested Viewpoint": {
            "type": "rich_text",
            "rich_text": [{"plain_text": ai_viewpoint}] if ai_viewpoint else [],
        },
        "Bookmark": {
            "type": "relation",
            "relation": [{"id": pid} for pid in (bookmark_ids or [])],
        },
    }

    return {
        "id": page_id,
        "properties": properties,
        "last_edited_time": last_edited_time,
    }


class TestSessionTransformer:
    def test_transforms_full_page(self) -> None:
        page = _make_notion_page(bookmark_ids=["bk-001"])
        result = SessionTransformer().transform(page)

        assert result["notion_id"] == "session-001"
        assert result["title"] == "AI Policy Discussion"
        assert result["date"] == "2026-03-20"
        assert result["ai_suggested_viewpoint"] == "This discussion covers governance frameworks."
        assert result["bookmark_notion_id"] == "bk-001"
        assert result["last_edited_time"] == "2026-04-01T12:00:00.000Z"

    def test_handles_missing_optional_properties(self) -> None:
        page = _make_notion_page(date=None, ai_viewpoint="")
        result = SessionTransformer().transform(page)

        assert result["date"] is None
        assert result["ai_suggested_viewpoint"] == ""

    def test_bookmark_id_none_when_no_relation(self) -> None:
        page = _make_notion_page()
        result = SessionTransformer().transform(page)

        assert result["bookmark_notion_id"] is None

    def test_bookmark_id_picks_first_when_multiple(self) -> None:
        page = _make_notion_page(bookmark_ids=["bk-001", "bk-002"])
        result = SessionTransformer().transform(page)

        assert result["bookmark_notion_id"] == "bk-001"

    def test_empty_title_returns_empty_string(self) -> None:
        page = _make_notion_page()
        page["properties"]["Name"] = {"type": "title", "title": []}
        result = SessionTransformer().transform(page)

        assert result["title"] == ""

    def test_relation_ids_empty_when_not_relation_type(self) -> None:
        page = _make_notion_page()
        page["properties"]["Bookmark"] = {"type": "rich_text", "rich_text": []}
        result = SessionTransformer().transform(page)

        assert result["bookmark_notion_id"] is None

    def test_handles_completely_empty_properties(self) -> None:
        page = {"id": "empty-session", "properties": {}, "last_edited_time": "2026-04-01T00:00:00Z"}
        result = SessionTransformer().transform(page)

        assert result["notion_id"] == "empty-session"
        assert result["title"] == ""
        assert result["date"] is None
        assert result["ai_suggested_viewpoint"] == ""
        assert result["bookmark_notion_id"] is None

    def test_logs_property_keys_on_first_transform(self, caplog) -> None:
        SessionTransformer._logged_keys = False
        page = _make_notion_page()

        import logging
        with caplog.at_level(logging.INFO):
            SessionTransformer().transform(page)

        assert any("Session property" in record.message for record in caplog.records)
