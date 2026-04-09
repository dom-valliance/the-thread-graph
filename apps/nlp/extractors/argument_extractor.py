from __future__ import annotations

import json
import uuid

from models.extraction import ExtractionContext, ExtractedArgument
from extractors.base import BaseExtractor

ARGUMENT_TOOL = {
    "name": "store_arguments",
    "description": "Store the extracted arguments from the transcript.",
    "input_schema": {
        "type": "object",
        "properties": {
            "arguments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Clear, concise statement of the argument.",
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": ["supports", "challenges", "neutral"],
                        },
                        "strength": {
                            "type": "string",
                            "enum": ["strong", "moderate", "weak"],
                        },
                        "speaker": {
                            "type": "string",
                            "description": "Speaker name if identifiable.",
                        },
                        "position_id": {
                            "type": "string",
                            "description": "ID of a matched existing position, if applicable.",
                        },
                        "relationship_type": {
                            "type": "string",
                            "enum": ["SUPPORTS", "CHALLENGES", "EXTENDS", "REFINES"],
                        },
                    },
                    "required": ["text", "sentiment", "relationship_type"],
                },
            },
        },
        "required": ["arguments"],
    },
}


class ArgumentExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedArgument]:
        template = self._load_prompt("argument_extraction")
        prompt = self._build_prompt(template, transcript, context)

        if context.existing_positions:
            positions_text = "\n".join(
                f"- [{p.id}] {p.text}" for p in context.existing_positions
            )
            prompt += (
                f"\n\nExisting positions to match against:\n{positions_text}"
            )

        response = await self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=[ARGUMENT_TOOL],
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_response(response)

    def _parse_response(self, response: object) -> list[ExtractedArgument]:
        arguments: list[ExtractedArgument] = []
        for block in response.content:
            if block.type != "tool_use" or block.name != "store_arguments":
                continue
            raw_args = block.input.get("arguments", [])
            for raw in raw_args:
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
        return arguments
