from __future__ import annotations

from typing import TypedDict

from models.extraction import ExtractionContext


class ExtractionState(TypedDict, total=False):
    transcript: str
    context: ExtractionContext
    prompt: str
    results: list
