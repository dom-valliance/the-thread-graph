"""Prompt building for Thread Prep Brief generation.

Extracted from services/thread_prep_generator.py for use as a pure function
in the LangGraph prep graph.
"""

from __future__ import annotations


def build_prep_prompt(
    session_id: str,
    arc_number: int,
    arc_name: str,
    arc: dict[str, object],
    is_week1: bool,
    bookmarks: list[dict[str, object]],
    locked_positions: list[dict[str, object]],
    all_locked_positions: list[dict[str, object]],
) -> str:
    sections: list[str] = []

    # System context
    sections.append(
        "You are preparing a session brief for the Valliance Thread, a 12-week "
        "structured learning curriculum. Your output will be used directly by the "
        "session lead to run a 2.5-hour Friday session. Be specific, evidence-grounded, "
        "and opinionated. British English throughout.\n"
    )

    # Arc context
    sections.append(f"## Arc {arc_number}: {arc['name']}\n")
    sections.append(f"Focus: {arc['focus']}\n")

    if is_week1:
        sections.append(f"Generic Problem Question: {arc['week1_problem_q']}")
        sections.append(f"Generic Landscape Question: {arc['week1_landscape_q']}\n")
    else:
        sections.append(f"Position Question: {arc['week2_position_q']}\n")

    # PMF anchors
    problem_anchors = arc.get("pmf_anchors_problem", [])
    solution_anchors = arc.get("pmf_anchors_solution", [])
    if problem_anchors or solution_anchors:
        sections.append("## PMF Canvas Anchors\n")
        if problem_anchors:
            sections.append("Problem anchors:")
            for a in problem_anchors:
                sections.append(f"  - {a}")
        if solution_anchors:
            sections.append("Solution anchors:")
            for a in solution_anchors:
                sections.append(f"  - {a}")
        sections.append("")

    # Landscape players
    players = arc.get("landscape_players", [])
    if players:
        sections.append(
            "Landscape players to map: " + ", ".join(players) + "\n"
        )

    # Bookmarks
    sections.append(f"## Recent Bookmarks ({len(bookmarks)} found)\n")
    if not bookmarks:
        sections.append(
            "The haul is thin. Note this in your brief and flag that the team "
            "may not be bookmarking enough in this area.\n"
        )
    else:
        for i, bk in enumerate(bookmarks):
            entry = f"[{i + 1}] {bk.get('title', 'Untitled')}"
            if bk.get("source"):
                entry += f" (Source: {bk['source']})"
            if bk.get("date_added"):
                entry += f" [{bk['date_added']}]"
            sections.append(entry)
            if bk.get("ai_summary"):
                sections.append(f"    Summary: {bk['ai_summary']}")
            if bk.get("valliance_viewpoint"):
                sections.append(f"    Viewpoint: {bk['valliance_viewpoint']}")
            if bk.get("edge_or_foundational"):
                sections.append(f"    Type: {bk['edge_or_foundational']}")
            topics = bk.get("topic_names", [])
            if topics:
                sections.append(f"    Topics: {', '.join(topics)}")
            other_arcs = bk.get("other_arc_names", [])
            if other_arcs:
                sections.append(f"    Also in arcs: {', '.join(other_arcs)}")
            sections.append("")

    # Locked positions (for Flash checks and Week 2 context)
    if locked_positions:
        sections.append("## Locked Positions for This Arc\n")
        for pos in locked_positions:
            sections.append(f"- {pos.get('text', '')}")
            if pos.get("anti_position_text"):
                sections.append(f"  Anti-position: {pos['anti_position_text']}")
        sections.append("")

    if all_locked_positions:
        other_positions = [
            p for p in all_locked_positions
            if p.get("arc_number") != arc_number
        ]
        if other_positions:
            sections.append("## Locked Positions from Other Arcs (for Flash checks)\n")
            for pos in other_positions:
                sections.append(
                    f"- Arc {pos.get('arc_number')} ({pos.get('arc_name')}): "
                    f"{pos.get('text', '')}"
                )
            sections.append("")

    # Instruction
    if is_week1:
        sections.append(
            "## Your Task\n"
            "Produce a Week 1 (Problem + Landscape) prep brief. Use the "
            "produce_prep_brief tool to return your structured output.\n"
            "Sharpen both questions using the specific evidence above. "
            "Map each relevant bookmark to a PMF canvas anchor. "
            "Propose a specific steelman grounded in this week's evidence. "
            "Suggest 5-7 workshop grid criteria that emerge from the evidence. "
            "Assign reading by landscape player. "
            "Flag any bookmarks relevant to other arcs, and check whether "
            "any challenge a previously locked position."
        )
    else:
        sections.append(
            "## Your Task\n"
            "Produce a Week 2 (Position + Pitch) prep brief. Use the "
            "produce_prep_brief tool to return your structured output.\n"
            "Identify new evidence since the arc's Week 1. "
            "Surface objection fuel for the Ghost Prospect. "
            "Identify cross-arc bridge connections. "
            "Flag P1/V1 signals. "
            "Map relevant bookmarks. "
            "Check for potential Flashes against other arcs' locked positions."
        )

    return "\n".join(sections)
