from __future__ import annotations

from typing import Any, TypedDict


class PrepGraphState(TypedDict, total=False):
    session_id: str
    arc_number: int
    arc_name: str
    week_type: str
    bookmarks: list[dict]
    locked_positions: list[dict]
    all_locked_positions: list[dict]
    arc_data: dict
    is_week1: bool
    prompt: str
    llm_output: Any  # AIMessage during generation, dict after validation
    _api_key: str | None
