from __future__ import annotations

from sync.session_transformer import SessionTransformer


def _make_notion_page(
    *,
    page_id: str = "session-001",
    title: str = "AI Policy Discussion",
    transcript: str = "Sarah: Let us discuss the new AI policy framework.",
    summary: str = "A discussion about AI governance.",
    date: str | None = "2026-03-20",
    duration: int | None = 90,
    relation_theme_ids: list[str] | None = None,
    last_edited_time: str = "2026-04-01T12:00:00.000Z",
) -> dict:
    properties: dict = {
        "Name": {
            "type": "title",
            "title": [{"plain_text": title}],
        },
        "Transcript": {
            "type": "rich_text",
            "rich_text": [{"plain_text": transcript}] if transcript else [],
        },
        "Summary": {
            "type": "rich_text",
            "rich_text": [{"plain_text": summary}] if summary else [],
        },
        "Date": {
            "type": "date",
            "date": {"start": date} if date else None,
        },
        "Duration": {
            "type": "number",
            "number": duration,
        },
        "Valliance Theme": {
            "type": "relation",
            "relation": [{"id": pid} for pid in (relation_theme_ids or [])],
        },
    }

    return {
        "id": page_id,
        "properties": properties,
        "last_edited_time": last_edited_time,
    }


class TestSessionTransformer:
    def test_transforms_full_page(self) -> None:
        page = _make_notion_page()
        result = SessionTransformer().transform(page)

        assert result["notion_id"] == "session-001"
        assert result["title"] == "AI Policy Discussion"
        assert result["transcript"] == "Sarah: Let us discuss the new AI policy framework."
        assert result["summary"] == "A discussion about AI governance."
        assert result["date"] == "2026-03-20"
        assert result["duration"] == 90
        assert result["last_edited_time"] == "2026-04-01T12:00:00.000Z"

    def test_handles_missing_optional_properties(self) -> None:
        page = _make_notion_page(date=None, duration=None)
        result = SessionTransformer().transform(page)

        assert result["date"] is None
        assert result["duration"] is None

    def test_extracts_relation_ids(self) -> None:
        page = _make_notion_page(relation_theme_ids=["theme-page-1", "theme-page-2"])
        result = SessionTransformer().transform(page)

        assert result["theme_page_ids"] == ["theme-page-1", "theme-page-2"]

    def test_empty_title_returns_empty_string(self) -> None:
        page = _make_notion_page()
        page["properties"]["Name"] = {"type": "title", "title": []}
        result = SessionTransformer().transform(page)

        assert result["title"] == ""

    def test_empty_transcript_returns_empty_string(self) -> None:
        page = _make_notion_page(transcript="")
        page["properties"]["Transcript"] = {"type": "rich_text", "rich_text": []}
        result = SessionTransformer().transform(page)

        assert result["transcript"] == ""

    def test_number_cast_to_int(self) -> None:
        page = _make_notion_page(duration=45)
        page["properties"]["Duration"]["number"] = 45.0
        result = SessionTransformer().transform(page)

        assert result["duration"] == 45
        assert isinstance(result["duration"], int)

    def test_relation_ids_empty_when_not_relation_type(self) -> None:
        page = _make_notion_page()
        page["properties"]["Valliance Theme"] = {"type": "rich_text", "rich_text": []}
        result = SessionTransformer().transform(page)

        assert result["theme_page_ids"] == []

    def test_handles_completely_empty_properties(self) -> None:
        page = {"id": "empty-session", "properties": {}, "last_edited_time": "2026-04-01T00:00:00Z"}
        result = SessionTransformer().transform(page)

        assert result["notion_id"] == "empty-session"
        assert result["title"] == ""
        assert result["transcript"] == ""
        assert result["date"] is None
        assert result["duration"] is None
