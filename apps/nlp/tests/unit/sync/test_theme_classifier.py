from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import anthropic
import pytest

from sync.theme_classifier import ThemeClassifier


def _make_tool_response(classifications: list[dict[str, object]]) -> SimpleNamespace:
    tool_block = SimpleNamespace(
        type="tool_use",
        name="classify_theme",
        input={"classifications": classifications},
    )
    return SimpleNamespace(content=[tool_block])


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
    async def test_classifies_bookmarks_missing_theme(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_response([
                {"index": 0, "theme": "Agentic AI"},
            ])
        )

        bookmarks = [
            _make_bookmark("AI Agents for Due Diligence", topic_names=["AI", "Automation"]),
        ]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Agentic AI"

    async def test_skips_bookmarks_with_existing_theme(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_response([])
        )

        bookmarks = [
            _make_bookmark("Article 1", theme_name="Existing Theme"),
            _make_bookmark("Article 2", theme_name="Another Theme"),
        ]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Existing Theme"
        assert result[1]["theme_name"] == "Another Theme"
        mock_client.messages.create.assert_not_awaited()

    async def test_returns_original_list_when_all_have_themes(self) -> None:
        mock_client = AsyncMock()

        bookmarks = [
            _make_bookmark("Article", theme_name="Theme A"),
        ]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert result is bookmarks
        mock_client.messages.create.assert_not_awaited()

    async def test_handles_api_error_gracefully(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic.APIError(
                message="rate limited",
                request=None,
                body=None,
            )
        )

        bookmarks = [
            _make_bookmark("Article without theme"),
        ]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert "theme_name" not in result[0]

    async def test_only_classifies_bookmarks_with_non_empty_title(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_response([
                {"index": 0, "theme": "Data Science"},
            ])
        )

        bookmarks = [
            _make_bookmark(""),
            _make_bookmark("   "),
            _make_bookmark("Real Article", topic_names=["Data"]),
        ]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert "theme_name" not in result[0]
        assert "theme_name" not in result[1]
        assert result[2]["theme_name"] == "Data Science"

    async def test_includes_known_themes_in_prompt(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_response([{"index": 0, "theme": "Agentic AI"}])
        )

        bookmarks = [_make_bookmark("Test Article")]

        classifier = ThemeClassifier(mock_client, known_themes=["Agentic AI", "Consulting Craft"])
        await classifier.classify_batch(bookmarks)

        call_args = mock_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Agentic AI" in prompt
        assert "Consulting Craft" in prompt

    async def test_ignores_out_of_range_index(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_response([
                {"index": 0, "theme": "Valid Theme"},
                {"index": 99, "theme": "Should be ignored"},
            ])
        )

        bookmarks = [_make_bookmark("Single Article")]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Valid Theme"

    async def test_mixed_batch_only_classifies_missing(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_response([
                {"index": 0, "theme": "Inferred Theme"},
            ])
        )

        bookmarks = [
            _make_bookmark("Has Theme", theme_name="Existing"),
            _make_bookmark("Needs Theme", topic_names=["Topic A"]),
        ]

        classifier = ThemeClassifier(mock_client)
        result = await classifier.classify_batch(bookmarks)

        assert result[0]["theme_name"] == "Existing"
        assert result[1]["theme_name"] == "Inferred Theme"
