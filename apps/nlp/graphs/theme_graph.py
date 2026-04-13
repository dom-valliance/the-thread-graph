"""LangGraph StateGraph for theme classification of bookmarks."""

from __future__ import annotations

import logging
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs.llm import get_llm
from graphs.tool_schemas import ThemeClassifyToolInput

logger = logging.getLogger(__name__)


class ThemeClassifierState(TypedDict, total=False):
    bookmarks: list[dict]
    known_themes: list[str]
    needs_classification: list[tuple[int, dict]]
    skip: bool


def filter_bookmarks_node(state: ThemeClassifierState) -> dict:
    needs: list[tuple[int, dict]] = []
    for i, bk in enumerate(state["bookmarks"]):
        if not bk.get("theme_name") and bk.get("title", "").strip():
            needs.append((i, bk))

    return {
        "needs_classification": needs,
        "skip": len(needs) == 0,
    }


def _build_classify_prompt(
    items: list[tuple[int, dict]],
    known_themes: list[str],
) -> str:
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
    if known_themes:
        known_section = (
            "\n\nExisting themes in the system (prefer these where they fit):\n"
            + "\n".join(f"- {t}" for t in known_themes)
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
        "Use the ThemeClassifyToolInput tool to return your classifications."
    )


async def classify_node(state: ThemeClassifierState) -> dict:
    needs = state["needs_classification"]
    known_themes = state.get("known_themes", [])
    bookmarks = list(state["bookmarks"])

    prompt = _build_classify_prompt(needs, known_themes)

    try:
        llm = get_llm(max_tokens=2048).bind_tools(
            [ThemeClassifyToolInput], tool_choice="any"
        )
        response = await llm.ainvoke([HumanMessage(content=prompt)])

        for tool_call in response.tool_calls:
            if tool_call["name"] != "ThemeClassifyToolInput":
                continue
            for entry in tool_call["args"].get("classifications", []):
                idx = entry.get("index")
                theme = entry.get("theme")
                if idx is not None and theme and 0 <= idx < len(needs):
                    original_idx = needs[idx][0]
                    bookmarks[original_idx]["theme_name"] = theme

    except Exception:
        logger.warning(
            "Theme classification failed; bookmarks will sync without inferred themes.",
            exc_info=True,
        )

    return {"bookmarks": bookmarks}


def should_classify(state: ThemeClassifierState) -> str:
    return "skip" if state.get("skip", False) else "classify"


graph_builder = StateGraph(ThemeClassifierState)
graph_builder.add_node("filter_bookmarks", filter_bookmarks_node)
graph_builder.add_node("classify", classify_node)
graph_builder.add_edge(START, "filter_bookmarks")
graph_builder.add_conditional_edges("filter_bookmarks", should_classify, {
    "classify": "classify",
    "skip": END,
})
graph_builder.add_edge("classify", END)

theme_graph = graph_builder.compile()
