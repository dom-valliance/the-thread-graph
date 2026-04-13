"""LangGraph StateGraph for Thread Prep Brief generation."""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs.arc_data import ARC_DATA
from graphs.llm import get_llm
from graphs.prep_prompts import build_prep_prompt
from graphs.prep_state import PrepGraphState
from graphs.tool_schemas import Week1PrepBriefToolInput, Week2PrepBriefToolInput

logger = logging.getLogger(__name__)


def resolve_arc_node(state: PrepGraphState) -> dict:
    arc_number = state["arc_number"]
    arc = ARC_DATA.get(arc_number)
    if arc is None:
        raise ValueError(f"No arc structure data for arc {arc_number}")

    is_week1 = state["week_type"] == "problem_landscape"
    return {"arc_data": arc, "is_week1": is_week1}


def build_prompt_node(state: PrepGraphState) -> dict:
    prompt = build_prep_prompt(
        session_id=state["session_id"],
        arc_number=state["arc_number"],
        arc_name=state["arc_name"],
        arc=state["arc_data"],
        is_week1=state["is_week1"],
        bookmarks=state.get("bookmarks", []),
        locked_positions=state.get("locked_positions", []),
        all_locked_positions=state.get("all_locked_positions", []),
    )
    return {"prompt": prompt}


async def generate_brief_node(state: PrepGraphState) -> dict:
    is_week1 = state["is_week1"]
    tool_cls = Week1PrepBriefToolInput if is_week1 else Week2PrepBriefToolInput

    llm = get_llm(
        max_tokens=8192,
        anthropic_api_key=state.get("_api_key"),
    ).bind_tools([tool_cls], tool_choice="any")

    logger.info(
        "Generating %s prep brief for Arc %d (%s) with %d bookmarks",
        "Week 1" if is_week1 else "Week 2",
        state["arc_number"],
        state["arc_name"],
        len(state.get("bookmarks", [])),
    )

    response = await llm.ainvoke([HumanMessage(content=state["prompt"])])
    return {"llm_output": response}


def validate_output_node(state: PrepGraphState) -> dict:
    response = state["llm_output"]
    if not response.tool_calls:
        logger.warning("No tool_use block found in LLM response")
        raise RuntimeError("LLM did not produce a structured prep brief")

    return {"llm_output": response.tool_calls[0]["args"]}


graph_builder = StateGraph(PrepGraphState)
graph_builder.add_node("resolve_arc", resolve_arc_node)
graph_builder.add_node("build_prompt", build_prompt_node)
graph_builder.add_node("generate_brief", generate_brief_node)
graph_builder.add_node("validate_output", validate_output_node)
graph_builder.add_edge(START, "resolve_arc")
graph_builder.add_edge("resolve_arc", "build_prompt")
graph_builder.add_edge("build_prompt", "generate_brief")
graph_builder.add_edge("generate_brief", "validate_output")
graph_builder.add_edge("validate_output", END)

prep_graph = graph_builder.compile()
