from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from sync.theme_classifier import ThemeClassifier


def _make_bookmark(
    title: str,
    theme_name: str | None = None,
    topic_names: list[str] | None = None,
) -> dict[str, object]:
    bk: dict[str, object] = {"title": title, "topic_names": topic_names or []}
    if theme_name is not None:
        bk["theme_name"] = theme_name
    return bk


class TestThemeClassifier:
    @patch("sync.theme_classifier.theme_graph")
    async def test_classifies_bookmarks_missing_theme(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [
            _make_bookmark("AI Agents for Due Diligence", topic_names=["AI", "Automation"]),
        ]
        classified = [dict(bookmarks[0], theme_name="Agentic AI")]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": classified})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Agentic AI"
        mock_graph.ainvoke.assert_awaited_once()

    @patch("sync.theme_classifier.theme_graph")
    async def test_skips_bookmarks_with_existing_theme(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [
            _make_bookmark("Article 1", theme_name="Existing Theme"),
            _make_bookmark("Article 2", theme_name="Another Theme"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": bookmarks})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Existing Theme"
        assert result[1]["theme_name"] == "Another Theme"
        mock_graph.ainvoke.assert_awaited_once()

    @patch("sync.theme_classifier.theme_graph")
    async def test_returns_original_list_when_all_have_themes(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [
            _make_bookmark("Article", theme_name="Theme A"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": bookmarks})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert result == bookmarks
        mock_graph.ainvoke.assert_awaited_once()

    @patch("sync.theme_classifier.theme_graph")
    async def test_handles_graph_error_gracefully(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [
            _make_bookmark("Article without theme"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": bookmarks})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert "theme_name" not in result[0]

    @patch("sync.theme_classifier.theme_graph")
    async def test_only_classifies_bookmarks_with_non_empty_title(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [
            _make_bookmark(""),
            _make_bookmark("   "),
            _make_bookmark("Real Article", topic_names=["Data"]),
        ]
        classified = [
            bookmarks[0],
            bookmarks[1],
            dict(bookmarks[2], theme_name="Data Science"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": classified})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert "theme_name" not in result[0]
        assert "theme_name" not in result[1]
        assert result[2]["theme_name"] == "Data Science"

    @patch("sync.theme_classifier.theme_graph")
    async def test_passes_known_themes_to_graph(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [_make_bookmark("Test Article")]
        classified = [dict(bookmarks[0], theme_name="Agentic AI")]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": classified})

        classifier = ThemeClassifier(known_themes=["Agentic AI", "Consulting Craft"])
        await classifier.classify_batch(bookmarks)

        mock_graph.ainvoke.assert_awaited_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert "Agentic AI" in call_args["known_themes"]
        assert "Consulting Craft" in call_args["known_themes"]

    @patch("sync.theme_classifier.theme_graph")
    async def test_ignores_out_of_range_index(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [_make_bookmark("Single Article")]
        classified = [dict(bookmarks[0], theme_name="Valid Theme")]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": classified})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Valid Theme"

    @patch("sync.theme_classifier.theme_graph")
    async def test_mixed_batch_only_classifies_missing(
        self, mock_graph: AsyncMock
    ) -> None:
        bookmarks = [
            _make_bookmark("Has Theme", theme_name="Existing"),
            _make_bookmark("Needs Theme", topic_names=["Topic A"]),
        ]
        classified = [
            bookmarks[0],
            dict(bookmarks[1], theme_name="Inferred Theme"),
        ]
        mock_graph.ainvoke = AsyncMock(return_value={"bookmarks": classified})

        classifier = ThemeClassifier()
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Existing"
        assert result[1]["theme_name"] == "Inferred Theme"
