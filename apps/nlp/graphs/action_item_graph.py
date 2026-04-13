"""LangGraph StateGraph for action item extraction from transcripts."""

from __future__ import annotations

import uuid

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs.extraction_state import ExtractionState
from graphs.llm import get_llm
from graphs.prompt_utils import load_prompt, build_prompt
from graphs.tool_schemas import ActionItemToolInput
from models.extraction import ExtractedActionItem


def build_prompt_node(state: ExtractionState) -> dict:
    template = load_prompt("action_item_extraction")
    prompt = build_prompt(template, state["transcript"], state["context"])

    context = state["context"]
    if context.existing_people:
        people_text = "\n".join(
            f"- {p.name} ({p.email})" for p in context.existing_people
        )
        prompt += f"\n\nKnown team members:\n{people_text}"

    return {"prompt": prompt}


async def extract_node(state: ExtractionState) -> dict:
    llm = get_llm().bind_tools([ActionItemToolInput], tool_choice="any")
    response = await llm.ainvoke([HumanMessage(content=state["prompt"])])

    items: list[ExtractedActionItem] = []
    for tool_call in response.tool_calls:
        if tool_call["name"] != "ActionItemToolInput":
            continue
        for raw in tool_call["args"].get("action_items", []):
            items.append(
                ExtractedActionItem(
                    id=str(uuid.uuid4()),
                    text=raw["text"],
                    assignee=raw.get("assignee"),
                    due_date=raw.get("due_date"),
                )
            )

    return {"results": items}


graph_builder = StateGraph(ExtractionState)
graph_builder.add_node("build_prompt", build_prompt_node)
graph_builder.add_node("extract", extract_node)
graph_builder.add_edge(START, "build_prompt")
graph_builder.add_edge("build_prompt", "extract")
graph_builder.add_edge("extract", END)

action_item_graph = graph_builder.compile()
