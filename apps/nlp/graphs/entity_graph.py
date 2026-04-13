"""LangGraph StateGraph for entity extraction from transcripts."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs.extraction_state import ExtractionState
from graphs.llm import get_llm
from graphs.prompt_utils import load_prompt, build_prompt
from graphs.tool_schemas import EntityToolInput
from models.extraction import ExtractedEntity


def build_prompt_node(state: ExtractionState) -> dict:
    template = load_prompt("entity_recognition")
    prompt = build_prompt(template, state["transcript"], state["context"])

    context = state["context"]
    if context.existing_topics:
        prompt += f"\n\nKnown topics: {', '.join(context.existing_topics)}"

    if context.existing_players:
        prompt += f"\n\nKnown players/organisations: {', '.join(context.existing_players)}"

    if context.existing_people:
        people_text = "\n".join(
            f"- {p.name} ({p.email})" for p in context.existing_people
        )
        prompt += f"\n\nKnown people:\n{people_text}"

    return {"prompt": prompt}


async def extract_node(state: ExtractionState) -> dict:
    llm = get_llm().bind_tools([EntityToolInput], tool_choice="any")
    response = await llm.ainvoke([HumanMessage(content=state["prompt"])])

    entities: list[ExtractedEntity] = []
    for tool_call in response.tool_calls:
        if tool_call["name"] != "EntityToolInput":
            continue
        for raw in tool_call["args"].get("entities", []):
            entities.append(
                ExtractedEntity(
                    name=raw["name"],
                    entity_type=raw["entity_type"],
                    matched_id=raw.get("matched_id"),
                )
            )

    return {"results": entities}


graph_builder = StateGraph(ExtractionState)
graph_builder.add_node("build_prompt", build_prompt_node)
graph_builder.add_node("extract", extract_node)
graph_builder.add_edge(START, "build_prompt")
graph_builder.add_edge("build_prompt", "extract")
graph_builder.add_edge("extract", END)

entity_graph = graph_builder.compile()
