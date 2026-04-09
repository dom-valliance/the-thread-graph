from __future__ import annotations

import uuid

from models.extraction import ExtractionContext, ExtractedActionItem
from extractors.base import BaseExtractor

ACTION_ITEM_TOOL = {
    "name": "store_action_items",
    "description": "Store the extracted action items from the transcript.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Clear description of the action item.",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Person responsible, if identifiable.",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO 8601 format, if mentioned.",
                        },
                    },
                    "required": ["text"],
                },
            },
        },
        "required": ["action_items"],
    },
}


class ActionItemExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedActionItem]:
        template = self._load_prompt("action_item_extraction")
        prompt = self._build_prompt(template, transcript, context)

        if context.existing_people:
            people_text = "\n".join(
                f"- {p.name} ({p.email})" for p in context.existing_people
            )
            prompt += f"\n\nKnown team members:\n{people_text}"

        response = await self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=[ACTION_ITEM_TOOL],
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_response(response)

    def _parse_response(self, response: object) -> list[ExtractedActionItem]:
        items: list[ExtractedActionItem] = []
        for block in response.content:
            if block.type != "tool_use" or block.name != "store_action_items":
                continue
            raw_items = block.input.get("action_items", [])
            for raw in raw_items:
                items.append(
                    ExtractedActionItem(
                        id=str(uuid.uuid4()),
                        text=raw["text"],
                        assignee=raw.get("assignee"),
                        due_date=raw.get("due_date"),
                    )
                )
        return items
