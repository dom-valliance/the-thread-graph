"""LangGraph StateGraph for argument extraction from transcripts."""

from __future__ import annotations

import uuid

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs.extraction_state import ExtractionState
from graphs.llm import get_llm
from graphs.prompt_utils import load_prompt, build_prompt
from graphs.tool_schemas import ArgumentToolInput
from models.extraction import ExtractedArgument


def build_prompt_node(state: ExtractionState) -> dict:
    template = load_prompt("argument_extraction")
    prompt = build_prompt(template, state["transcript"], state["context"])

    context = state["context"]
    if context.existing_positions:
        positions_text = "\n".join(
            f"- [{p.id}] {p.text}" for p in context.existing_positions
        )
        prompt += f"\n\nExisting positions to match against:\n{positions_text}"

    return {"prompt": prompt}


async def extract_node(state: ExtractionState) -> dict:
    llm = get_llm().bind_tools([ArgumentToolInput], tool_choice="any")
    response = await llm.ainvoke([HumanMessage(content=state["prompt"])])

    arguments: list[ExtractedArgument] = []
    for tool_call in response.tool_calls:
        if tool_call["name"] != "ArgumentToolInput":
            continue
        for raw in tool_call["args"].get("arguments", []):
            arguments.append(
                ExtractedArgument(
                    id=str(uuid.uuid4()),
                    text=raw["text"],
                    sentiment=raw["sentiment"],
                    strength=raw.get("strength"),
                    speaker=raw.get("speaker"),
                    position_id=raw.get("position_id"),
                    relationship_type=raw["relationship_type"],
                )
            )

    return {"results": arguments}


graph_builder = StateGraph(ExtractionState)
graph_builder.add_node("build_prompt", build_prompt_node)
graph_builder.add_node("extract", extract_node)
graph_builder.add_edge(START, "build_prompt")
graph_builder.add_edge("build_prompt", "extract")
graph_builder.add_edge("extract", END)

argument_graph = graph_builder.compile()
