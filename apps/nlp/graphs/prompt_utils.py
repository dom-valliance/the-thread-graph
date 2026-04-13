from __future__ import annotations

from pathlib import Path

from models.extraction import ExtractionContext

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    return prompt_path.read_text()


def build_prompt(template: str, transcript: str, context: ExtractionContext) -> str:
    return (
        template.replace("{{TRANSCRIPT}}", transcript)
        .replace("{{ARC_NAME}}", context.arc_name or "Unknown")
        .replace("{{SESSION_ID}}", context.session_id)
    )
