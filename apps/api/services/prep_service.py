from __future__ import annotations

import json
import logging
from uuid import uuid4

from core.exceptions import ConflictError, NotFoundError
from models.prep import (
    PrepBriefBookmark,
    PrepBriefResponse,
    ReadingAssignmentCreate,
    ReadingAssignmentResponse,
    ReadingAssignmentUpdate,
    WorkshopAssignmentCreate,
    WorkshopAssignmentResponse,
    WorkshopAssignmentUpdate,
)
from models.thread_prep import ThreadPrepBriefResponse
from repositories.cycle_repository import CycleRepository
from repositories.prep_repository import PrepRepository
from repositories.thread_prep_repository import ThreadPrepRepository
from services.thread_prep_generator import PrepContext, ThreadPrepGenerator

logger = logging.getLogger(__name__)


class PrepService:
    def __init__(
        self,
        repository: PrepRepository,
        thread_prep_repo: ThreadPrepRepository | None = None,
        cycle_repo: CycleRepository | None = None,
        generator: ThreadPrepGenerator | None = None,
    ) -> None:
        self._repo = repository
        self._thread_prep_repo = thread_prep_repo
        self._cycle_repo = cycle_repo
        self._generator = generator

    async def create_workshop_assignment(
        self, session_id: str, data: WorkshopAssignmentCreate
    ) -> WorkshopAssignmentResponse:
        assignment_id = str(uuid4())
        row = await self._repo.create_workshop_assignment({
            "id": assignment_id,
            "player_or_approach": data.player_or_approach,
            "assigned_to_email": data.assigned_to_email,
            "session_id": session_id,
        })
        if row is None:
            raise NotFoundError("Session or person not found")
        return WorkshopAssignmentResponse(**row)

    async def list_workshop_assignments(
        self, session_id: str
    ) -> list[WorkshopAssignmentResponse]:
        rows = await self._repo.list_workshop_assignments(session_id)
        return [WorkshopAssignmentResponse(**row) for row in rows]

    async def update_workshop_assignment(
        self, assignment_id: str, data: WorkshopAssignmentUpdate
    ) -> WorkshopAssignmentResponse:
        update_data = data.model_dump(exclude_none=True)
        row = await self._repo.update_workshop_assignment(assignment_id, update_data)
        if row is None:
            raise NotFoundError(f"Workshop assignment '{assignment_id}' not found")
        return WorkshopAssignmentResponse(**row)

    async def create_reading_assignment(
        self, session_id: str, data: ReadingAssignmentCreate
    ) -> ReadingAssignmentResponse:
        assignment_id = str(uuid4())
        row = await self._repo.create_reading_assignment({
            "id": assignment_id,
            "bookmark_notion_id": data.bookmark_notion_id,
            "assigned_to_email": data.assigned_to_email,
            "session_id": session_id,
        })
        if row is None:
            raise NotFoundError("Session, person, or bookmark not found")
        return ReadingAssignmentResponse(**row)

    async def list_reading_assignments(
        self, session_id: str
    ) -> list[ReadingAssignmentResponse]:
        rows = await self._repo.list_reading_assignments(session_id)
        return [ReadingAssignmentResponse(**row) for row in rows]

    async def update_reading_assignment(
        self, assignment_id: str, data: ReadingAssignmentUpdate
    ) -> ReadingAssignmentResponse:
        row = await self._repo.update_reading_assignment(
            assignment_id, data.status
        )
        if row is None:
            raise NotFoundError(f"Reading assignment '{assignment_id}' not found")
        return ReadingAssignmentResponse(**row)

    async def get_prep_brief(self, session_id: str) -> PrepBriefResponse:
        row = await self._repo.get_prep_brief(session_id)
        if row is None:
            raise NotFoundError(f"Session '{session_id}' not found")
        return PrepBriefResponse(
            session_id=row["session_id"],
            arc_name=row["arc_name"],
            recent_bookmarks=[
                PrepBriefBookmark(**b) for b in row["recent_bookmarks"]
            ],
            previous_locked_position_text=row["previous_locked_position_text"],
            evidence_count=row["evidence_count"],
        )

    # ------------------------------------------------------------------
    # Thread Prep Brief (LLM-generated)
    # ------------------------------------------------------------------

    async def get_thread_prep(self, session_id: str) -> ThreadPrepBriefResponse:
        if self._thread_prep_repo is None:
            raise NotFoundError("Thread prep not configured")
        row = await self._thread_prep_repo.get_brief_for_session(session_id)
        if row is None:
            raise NotFoundError(f"No thread prep brief for session '{session_id}'")
        return ThreadPrepBriefResponse(**row)

    async def generate_thread_prep(
        self, session_id: str
    ) -> ThreadPrepBriefResponse:
        if self._thread_prep_repo is None or self._cycle_repo is None:
            raise NotFoundError("Thread prep not configured")
        if self._generator is None:
            raise NotFoundError("Anthropic API key not configured")

        # Check if one already exists
        existing = await self._thread_prep_repo.get_brief_for_session(session_id)
        if existing is not None:
            raise ConflictError(
                f"A thread prep brief already exists for session '{session_id}'. "
                "Use the regenerate endpoint to replace it."
            )

        return await self._do_generate(session_id)

    async def regenerate_thread_prep(
        self, session_id: str
    ) -> ThreadPrepBriefResponse:
        if self._thread_prep_repo is None or self._cycle_repo is None:
            raise NotFoundError("Thread prep not configured")
        if self._generator is None:
            raise NotFoundError("Anthropic API key not configured")

        await self._thread_prep_repo.delete_brief_for_session(session_id)
        return await self._do_generate(session_id)

    async def _do_generate(self, session_id: str) -> ThreadPrepBriefResponse:
        # Fetch session info
        session = await self._cycle_repo.get_scheduled_session(session_id)
        if session is None:
            raise NotFoundError(f"Scheduled session '{session_id}' not found")

        arc_number = session["arc_number"]
        arc_name = session.get("arc_name", f"Arc {arc_number}")
        week_type = session["week_type"]

        # Fetch bookmarks (try 14 days, fall back to 21)
        bookmarks = await self._thread_prep_repo.get_bookmarks_for_prep(
            arc_number, days_back=14
        )
        if len(bookmarks) < 3:
            bookmarks = await self._thread_prep_repo.get_bookmarks_for_prep(
                arc_number, days_back=21
            )

        # Fetch positions for context
        locked_positions = await self._thread_prep_repo.get_locked_positions_for_arc(
            arc_number
        )
        all_locked = await self._thread_prep_repo.get_all_locked_positions()

        # Build context and generate
        ctx = PrepContext(
            session_id=session_id,
            arc_number=arc_number,
            arc_name=arc_name,
            week_type=week_type,
            bookmarks=bookmarks,
            locked_positions=locked_positions,
            all_locked_positions=all_locked,
        )

        llm_output = await self._generator.generate(ctx)

        # Build markdown summary
        raw_markdown = _build_markdown(llm_output, ctx)

        # Persist
        brief_id = str(uuid4())
        bookmark_notion_ids = [
            bk.get("notion_id") for bk in bookmarks if bk.get("notion_id")
        ]

        persist_data = {
            "id": brief_id,
            "session_id": session_id,
            "week_type": week_type,
            "arc_number": arc_number,
            "arc_name": arc_name,
            "sharpened_problem_question": llm_output.get("sharpened_problem_question"),
            "problem_question_rationale": llm_output.get("problem_question_rationale"),
            "sharpened_landscape_question": llm_output.get("sharpened_landscape_question"),
            "landscape_question_rationale": llm_output.get("landscape_question_rationale"),
            "steelman_argument": llm_output.get("steelman_argument"),
            "steelman_rationale": llm_output.get("steelman_rationale"),
            "workshop_grid_criteria_json": json.dumps(
                llm_output.get("workshop_grid_criteria", [])
            ),
            "new_evidence_since_week1": llm_output.get("new_evidence_since_week1"),
            "objection_fuel": llm_output.get("objection_fuel"),
            "cross_arc_bridge_prompts": llm_output.get("cross_arc_bridge_prompts"),
            "p1_v1_signal": llm_output.get("p1_v1_signal"),
            "bookmark_anchor_mapping_json": json.dumps(
                llm_output.get("bookmark_anchor_mapping", [])
            ),
            "reading_assignments_json": json.dumps(
                llm_output.get("reading_assignments", [])
            ),
            "adjacent_bookmarks_json": json.dumps(
                llm_output.get("adjacent_bookmarks", [])
            ),
            "flash_checks_json": json.dumps(
                llm_output.get("flash_checks", [])
            ),
            "bookmark_count": len(bookmarks),
            "raw_markdown": raw_markdown,
            "status": "complete",
            "bookmark_notion_ids": bookmark_notion_ids,
        }

        row = await self._thread_prep_repo.create_brief(persist_data)
        if row is None:
            raise NotFoundError("Failed to persist thread prep brief")
        return ThreadPrepBriefResponse(**row)


def _build_markdown(output: dict[str, object], ctx: PrepContext) -> str:
    """Build a human-readable markdown summary of the prep brief."""
    lines: list[str] = []
    lines.append(f"# Thread Prep: Arc {ctx.arc_number} ({ctx.arc_name})")
    lines.append(f"**Week type:** {'Problem + Landscape' if ctx.week_type == 'problem_landscape' else 'Position + Pitch'}")
    lines.append(f"**Bookmarks used:** {len(ctx.bookmarks)}")
    lines.append("")

    if ctx.week_type == "problem_landscape":
        if output.get("sharpened_problem_question"):
            lines.append("## Sharpened Problem Question")
            lines.append(output["sharpened_problem_question"])
            if output.get("problem_question_rationale"):
                lines.append(f"\n_{output['problem_question_rationale']}_")
            lines.append("")

        if output.get("sharpened_landscape_question"):
            lines.append("## Sharpened Landscape Question")
            lines.append(output["sharpened_landscape_question"])
            if output.get("landscape_question_rationale"):
                lines.append(f"\n_{output['landscape_question_rationale']}_")
            lines.append("")

        if output.get("steelman_argument"):
            lines.append("## Steelman")
            lines.append(f"> {output['steelman_argument']}")
            if output.get("steelman_rationale"):
                lines.append(f"\n_{output['steelman_rationale']}_")
            lines.append("")

        criteria = output.get("workshop_grid_criteria", [])
        if criteria:
            lines.append("## Workshop Grid Criteria")
            lines.append("| Criterion | What it tests |")
            lines.append("|-----------|--------------|")
            for c in criteria:
                lines.append(f"| {c.get('criterion', '')} | {c.get('what_it_tests', '')} |")
            lines.append("")
    else:
        for field, heading in [
            ("new_evidence_since_week1", "New Evidence Since Week 1"),
            ("objection_fuel", "Objection Fuel"),
            ("cross_arc_bridge_prompts", "Cross-Arc Bridge Prompts"),
            ("p1_v1_signal", "P1/V1 Signal"),
        ]:
            if output.get(field):
                lines.append(f"## {heading}")
                lines.append(output[field])
                lines.append("")

    mapping = output.get("bookmark_anchor_mapping", [])
    if mapping:
        lines.append("## Bookmark-to-Anchor Mapping")
        lines.append("| Bookmark | PMF Anchor | Contribution |")
        lines.append("|----------|-----------|-------------|")
        for m in mapping:
            title = m.get("bookmark_title", "")
            source = m.get("bookmark_source", "")
            label = f"{title} ({source})" if source else title
            lines.append(f"| {label} | {m.get('pmf_anchor', '')} | {m.get('contribution', '')} |")
        lines.append("")

    assignments = output.get("reading_assignments", [])
    if assignments:
        lines.append("## Reading Assignments")
        for a in assignments:
            titles = ", ".join(a.get("bookmark_titles", []))
            lines.append(f"- **{a.get('player', '')}:** {titles}")
        lines.append("")

    flashes = output.get("flash_checks", [])
    if flashes:
        lines.append("## Potential Flashes")
        for f in flashes:
            lines.append(
                f"- **{f.get('bookmark_title', '')}** challenges "
                f"Arc {f.get('challenged_arc', '')} on: {f.get('challenged_claim', '')}"
            )
        lines.append("")

    return "\n".join(lines)
