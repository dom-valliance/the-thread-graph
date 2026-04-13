"""LangGraph StateGraph for evidence extraction from transcripts."""

from __future__ import annotations

import uuid

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs.extraction_state import ExtractionState
from graphs.llm import get_llm
from graphs.prompt_utils import load_prompt, build_prompt
from graphs.tool_schemas import EvidenceToolInput
from models.extraction import ExtractedEvidence


def build_prompt_node(state: ExtractionState) -> dict:
    template = load_prompt("evidence_identification")
    prompt = build_prompt(template, state["transcript"], state["context"])

    context = state["context"]
    if context.existing_positions:
        positions_text = "\n".join(
            f"- [{p.id}] {p.text}" for p in context.existing_positions
        )
        prompt += f"\n\nExisting positions to link evidence to:\n{positions_text}"

    return {"prompt": prompt}


async def extract_node(state: ExtractionState) -> dict:
    llm = get_llm().bind_tools([EvidenceToolInput], tool_choice="any")
    response = await llm.ainvoke([HumanMessage(content=state["prompt"])])

    evidence_list: list[ExtractedEvidence] = []
    for tool_call in response.tool_calls:
        if tool_call["name"] != "EvidenceToolInput":
            continue
        for raw in tool_call["args"].get("evidence", []):
            evidence_list.append(
                ExtractedEvidence(
                    id=str(uuid.uuid4()),
                    text=raw["text"],
                    type=raw["type"],
                    source_bookmark_id=raw.get("source_bookmark_id"),
                    position_id=raw.get("position_id"),
                )
            )

    return {"results": evidence_list}


graph_builder = StateGraph(ExtractionState)
graph_builder.add_node("build_prompt", build_prompt_node)
graph_builder.add_node("extract", extract_node)
graph_builder.add_edge(START, "build_prompt")
graph_builder.add_edge("build_prompt", "extract")
graph_builder.add_edge("extract", END)

evidence_graph = graph_builder.compile()
