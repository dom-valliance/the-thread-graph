from __future__ import annotations

from models.extraction import ExtractionContext, ExtractedEntity
from extractors.base import BaseExtractor

ENTITY_TOOL = {
    "name": "store_entities",
    "description": "Store the extracted entities from the transcript.",
    "input_schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the entity.",
                        },
                        "entity_type": {
                            "type": "string",
                            "enum": ["person", "topic", "player"],
                        },
                        "matched_id": {
                            "type": "string",
                            "description": "ID of a matched existing entity, if applicable.",
                        },
                    },
                    "required": ["name", "entity_type"],
                },
            },
        },
        "required": ["entities"],
    },
}


class EntityExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedEntity]:
        template = self._load_prompt("entity_recognition")
        prompt = self._build_prompt(template, transcript, context)

        if context.existing_topics:
            prompt += f"\n\nKnown topics: {', '.join(context.existing_topics)}"

        if context.existing_players:
            prompt += f"\n\nKnown players/organisations: {', '.join(context.existing_players)}"

        if context.existing_people:
            people_text = "\n".join(
                f"- {p.name} ({p.email})" for p in context.existing_people
            )
            prompt += f"\n\nKnown people:\n{people_text}"

        response = await self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=[ENTITY_TOOL],
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_response(response)

    def _parse_response(self, response: object) -> list[ExtractedEntity]:
        entities: list[ExtractedEntity] = []
        for block in response.content:
            if block.type != "tool_use" or block.name != "store_entities":
                continue
            raw_items = block.input.get("entities", [])
            for raw in raw_items:
                entities.append(
                    ExtractedEntity(
                        name=raw["name"],
                        entity_type=raw["entity_type"],
                        matched_id=raw.get("matched_id"),
                    )
                )
        return entities
