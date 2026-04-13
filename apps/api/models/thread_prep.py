from __future__ import annotations

from pydantic import BaseModel


class BookmarkAnchorMapping(BaseModel):
    bookmark_title: str
    bookmark_source: str | None = None
    pmf_anchor: str
    contribution: str


class WorkshopCriterion(BaseModel):
    criterion: str
    what_it_tests: str


class ReadingAssignment(BaseModel):
    player: str
    bookmark_titles: list[str]


class AdjacentBookmark(BaseModel):
    bookmark_title: str
    relevant_arc: str
    reason: str


class FlashCheck(BaseModel):
    bookmark_title: str
    challenged_arc: str
    challenged_claim: str


class ThreadPrepBriefResponse(BaseModel):
    id: str
    session_id: str
    week_type: str
    arc_number: int
    arc_name: str

    # Week 1 fields
    sharpened_problem_question: str | None = None
    problem_question_rationale: str | None = None
    sharpened_landscape_question: str | None = None
    landscape_question_rationale: str | None = None
    steelman_argument: str | None = None
    steelman_rationale: str | None = None
    workshop_grid_criteria: list[WorkshopCriterion] = []

    # Week 2 fields
    new_evidence_since_week1: str | None = None
    objection_fuel: str | None = None
    cross_arc_bridge_prompts: str | None = None
    p1_v1_signal: str | None = None

    # Common
    bookmark_anchor_mapping: list[BookmarkAnchorMapping] = []
    reading_assignments: list[ReadingAssignment] = []
    adjacent_bookmarks: list[AdjacentBookmark] = []
    flash_checks: list[FlashCheck] = []
    bookmark_count: int = 0
    raw_markdown: str = ""

    status: str = "complete"
    created_at: str
    updated_at: str
