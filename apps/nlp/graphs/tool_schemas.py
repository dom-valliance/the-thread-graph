"""Pydantic models mirroring the Anthropic tool input_schema definitions.

Used with ChatAnthropic.bind_tools() for structured output extraction.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# -- Argument extraction -------------------------------------------------------

class ArgumentItem(BaseModel):
    text: str
    sentiment: str  # supports | challenges | neutral
    strength: str | None = None
    speaker: str | None = None
    position_id: str | None = None
    relationship_type: str  # SUPPORTS | CHALLENGES | EXTENDS | REFINES


class ArgumentToolInput(BaseModel):
    """Store the extracted arguments from the transcript."""
    arguments: list[ArgumentItem]


# -- Action item extraction ----------------------------------------------------

class ActionItemItem(BaseModel):
    text: str
    assignee: str | None = None
    due_date: str | None = None


class ActionItemToolInput(BaseModel):
    """Store the extracted action items from the transcript."""
    action_items: list[ActionItemItem]


# -- Evidence extraction -------------------------------------------------------

class EvidenceItem(BaseModel):
    text: str
    type: str  # citation | anecdote | data_point | expert_opinion | case_study
    source_bookmark_id: str | None = None
    position_id: str | None = None


class EvidenceToolInput(BaseModel):
    """Store the extracted evidence from the transcript."""
    evidence: list[EvidenceItem]


# -- Entity extraction ---------------------------------------------------------

class EntityItem(BaseModel):
    name: str
    entity_type: str  # person | topic | player
    matched_id: str | None = None


class EntityToolInput(BaseModel):
    """Store the extracted entities from the transcript."""
    entities: list[EntityItem]


# -- Theme classification ------------------------------------------------------

class ThemeClassification(BaseModel):
    index: int
    theme: str


class ThemeClassifyToolInput(BaseModel):
    """Classify bookmarks into themes based on their topics and titles."""
    classifications: list[ThemeClassification]
