from __future__ import annotations

import uuid

from models.extraction import ExtractionContext, ExtractedEvidence
from extractors.base import BaseExtractor

EVIDENCE_TOOL = {
    "name": "store_evidence",
    "description": "Store the extracted evidence from the transcript.",
    "input_schema": {
        "type": "object",
        "properties": {
            "evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The evidence statement or reference.",
                        },
                        "type": {
                            "type": "string",
                            "enum": [
                                "citation",
                                "anecdote",
                                "data_point",
                                "expert_opinion",
                                "case_study",
                            ],
                        },
                        "source_bookmark_id": {
                            "type": "string",
                            "description": "ID of a matched existing bookmark, if applicable.",
                        },
                        "position_id": {
                            "type": "string",
                            "description": "ID of the position this evidence supports.",
                        },
                    },
                    "required": ["text", "type"],
                },
            },
        },
        "required": ["evidence"],
    },
}


class EvidenceExtractor(BaseExtractor):
    async def extract(
        self, transcript: str, context: ExtractionContext
    ) -> list[ExtractedEvidence]:
        template = self._load_prompt("evidence_identification")
        prompt = self._build_prompt(template, transcript, context)

        if context.existing_positions:
            positions_text = "\n".join(
                f"- [{p.id}] {p.text}" for p in context.existing_positions
            )
            prompt += f"\n\nExisting positions to link evidence to:\n{positions_text}"

        response = await self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=[EVIDENCE_TOOL],
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_response(response)

    def _parse_response(self, response: object) -> list[ExtractedEvidence]:
        evidence_list: list[ExtractedEvidence] = []
        for block in response.content:
            if block.type != "tool_use" or block.name != "store_evidence":
                continue
            raw_items = block.input.get("evidence", [])
            for raw in raw_items:
                evidence_list.append(
                    ExtractedEvidence(
                        id=str(uuid.uuid4()),
                        text=raw["text"],
                        type=raw["type"],
                        source_bookmark_id=raw.get("source_bookmark_id"),
                        position_id=raw.get("position_id"),
                    )
                )
        return evidence_list
