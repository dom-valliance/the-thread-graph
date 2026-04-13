"""Thread Prep Brief generator using LangGraph.

Delegates to graphs/prep_graph.py for the actual LLM orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass

from graphs.prep_graph import prep_graph


@dataclass
class PrepContext:
    session_id: str
    arc_number: int
    arc_name: str
    week_type: str
    bookmarks: list[dict[str, object]]
    locked_positions: list[dict[str, object]]
    all_locked_positions: list[dict[str, object]]


class ThreadPrepGenerator:
    """Generates structured Thread Prep Briefs using LangGraph."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate(self, ctx: PrepContext) -> dict[str, object]:
        result = await prep_graph.ainvoke({
            "session_id": ctx.session_id,
            "arc_number": ctx.arc_number,
            "arc_name": ctx.arc_name,
            "week_type": ctx.week_type,
            "bookmarks": ctx.bookmarks,
            "locked_positions": ctx.locked_positions,
            "all_locked_positions": ctx.all_locked_positions,
            "_api_key": self._api_key,
        })
        return result["llm_output"]
