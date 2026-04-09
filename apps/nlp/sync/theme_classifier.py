from __future__ import annotations

import logging

import anthropic

logger = logging.getLogger(__name__)

CLASSIFY_THEME_TOOL = {
    "name": "classify_theme",
    "description": "Classify bookmarks into themes based on their topics and titles.",
    "input_schema": {
        "type": "object",
        "properties": {
            "classifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "integer",
                            "description": "Zero-based index of the bookmark in the input list.",
                        },
                        "theme": {
                            "type": "string",
                            "description": "The theme name for this bookmark.",
                        },
                    },
                    "required": ["index", "theme"],
                },
            },
        },
        "required": ["classifications"],
    },
}


class ThemeClassifier:
    """Uses an LLM to classify bookmarks into themes when Valliance Themes is not set."""

    def __init__(self, client: anthropic.AsyncAnthropic, known_themes: list[str] | None = None) -> None:
        self._client = client
        self._known_themes = known_themes or []

    async def classify_batch(
        self, bookmarks: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        """For bookmarks missing a theme_name, infer one from topics and title.

        Mutates and returns the same list. Bookmarks that already have a
        theme_name are left untouched.
        """
        needs_classification: list[tuple[int, dict[str, object]]] = []
        for i, bk in enumerate(bookmarks):
            if not bk.get("theme_name") and bk.get("title", "").strip():
                needs_classification.append((i, bk))

        if not needs_classification:
            return bookmarks

        prompt = self._build_prompt(needs_classification)

        try:
            response = await self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                tools=[CLASSIFY_THEME_TOOL],
                messages=[{"role": "user", "content": prompt}],
            )

            for block in response.content:
                if block.type != "tool_use" or block.name != "classify_theme":
                    continue
                for entry in block.input.get("classifications", []):
                    idx = entry.get("index")
                    theme = entry.get("theme")
                    if idx is not None and theme and 0 <= idx < len(needs_classification):
                        original_idx = needs_classification[idx][0]
                        bookmarks[original_idx]["theme_name"] = theme

        except anthropic.APIError:
            logger.warning("Theme classification failed; bookmarks will sync without inferred themes.", exc_info=True)

        return bookmarks

    def _build_prompt(self, items: list[tuple[int, dict[str, object]]]) -> str:
        lines = []
        for local_idx, (_, bk) in enumerate(items):
            topics = ", ".join(bk.get("topic_names", []))
            title = bk.get("title", "Untitled")
            if topics:
                lines.append(f"[{local_idx}] Title: {title} | Topics: {topics}")
            else:
                lines.append(f"[{local_idx}] Title: {title}")

        bookmark_list = "\n".join(lines)

        known_section = ""
        if self._known_themes:
            known_section = (
                "\n\nExisting themes in the system (prefer these where they fit):\n"
                + "\n".join(f"- {t}" for t in self._known_themes)
            )

        return (
            "You are classifying bookmarks into themes for a knowledge graph.\n"
            "Each bookmark has a title and optionally a set of topics. Based on these, "
            "assign a single short theme name (2-4 words) that captures the overarching "
            "category. When topics are missing, infer the theme from the title.\n"
            "Reuse the same theme name for bookmarks that belong together.\n"
            f"{known_section}\n\n"
            "Bookmarks to classify:\n"
            f"{bookmark_list}\n\n"
            "Use the classify_theme tool to return your classifications."
        )
