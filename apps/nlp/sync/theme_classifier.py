from __future__ import annotations

from graphs.theme_graph import theme_graph


class ThemeClassifier:
    """Uses a LangGraph agent to classify bookmarks into themes."""

    def __init__(self, known_themes: list[str] | None = None) -> None:
        self._known_themes = known_themes or []

    async def classify_batch(
        self, bookmarks: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        result = await theme_graph.ainvoke({
            "bookmarks": bookmarks,
            "known_themes": self._known_themes,
        })
        return result["bookmarks"]
