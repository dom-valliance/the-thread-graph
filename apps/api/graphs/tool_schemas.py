"""Pydantic models mirroring the Week 1 / Week 2 prep tool schemas.

Used with ChatAnthropic.bind_tools() for structured output extraction.
"""

from __future__ import annotations

from pydantic import BaseModel


# -- Week 1 (Problem + Landscape) ---------------------------------------------

class BookmarkAnchorMapping(BaseModel):
    bookmark_title: str
    bookmark_source: str | None = None
    pmf_anchor: str
    contribution: str


class WorkshopGridCriterion(BaseModel):
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


class Week1PrepBriefToolInput(BaseModel):
    """Produce a structured Week 1 (Problem + Landscape) session prep brief for the Valliance Thread."""
    sharpened_problem_question: str
    problem_question_rationale: str
    sharpened_landscape_question: str
    landscape_question_rationale: str
    bookmark_anchor_mapping: list[BookmarkAnchorMapping]
    steelman_argument: str
    steelman_rationale: str
    workshop_grid_criteria: list[WorkshopGridCriterion]
    reading_assignments: list[ReadingAssignment]
    adjacent_bookmarks: list[AdjacentBookmark] | None = None
    flash_checks: list[FlashCheck] | None = None


# -- Week 2 (Position + Pitch) ------------------------------------------------

class Week2PrepBriefToolInput(BaseModel):
    """Produce a structured Week 2 (Position + Pitch) session prep brief for the Valliance Thread."""
    new_evidence_since_week1: str
    objection_fuel: str
    cross_arc_bridge_prompts: str
    p1_v1_signal: str
    bookmark_anchor_mapping: list[BookmarkAnchorMapping]
    reading_assignments: list[ReadingAssignment]
    adjacent_bookmarks: list[AdjacentBookmark] | None = None
    flash_checks: list[FlashCheck] | None = None
