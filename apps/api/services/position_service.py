from __future__ import annotations

from uuid import uuid4

from core.exceptions import ConflictError, NotFoundError, ValidationError
from models.position import (
    ArgumentMapResponse,
    ArgumentSummary,
    EvidenceChainItem,
    EvidenceTrailItem,
    EvidenceTrailBookmark,
    EvidenceTrailResponse,
    ObjectionPair,
    PositionCreate,
    PositionDetail,
    PositionLock,
    PositionResponse,
    PositionRevise,
    PositionUpdate,
    PositionVersionResponse,
    SteelmanItem,
)
from repositories.position_repository import PositionRepository


class PositionService:
    def __init__(self, repository: PositionRepository) -> None:
        self._repo = repository

    async def list_positions(
        self,
        arc_number: int | None = None,
        status: str | None = None,
        proposition: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[PositionResponse]:
        rows = await self._repo.list_positions(
            arc_number=arc_number,
            status=status,
            proposition=proposition,
            cursor=cursor,
            limit=limit,
        )
        return [PositionResponse(**row) for row in rows]

    async def get_position_detail(self, position_id: str) -> PositionDetail:
        row = await self._repo.get_position(position_id)
        if row is None:
            raise NotFoundError(f"Position {position_id} not found")
        return PositionDetail(
            **{k: v for k, v in row.items() if k not in (
                "anti_position", "evidence_chain",
                "supporting_arguments", "challenging_arguments",
            )},
            anti_position=row["anti_position"],
            evidence_chain=[
                EvidenceChainItem(**e) for e in row["evidence_chain"]
            ],
            supporting_arguments=[
                ArgumentSummary(**a) for a in row["supporting_arguments"]
            ],
            challenging_arguments=[
                ArgumentSummary(**a) for a in row["challenging_arguments"]
            ],
        )

    async def create_position(self, data: PositionCreate) -> PositionResponse:
        position_id = str(uuid4())
        row = await self._repo.create_position({
            "id": position_id,
            "text": data.text,
            "arc_number": data.arc_number,
            "session_id": data.session_id,
            "anti_position_text": data.anti_position_text,
            "cross_arc_bridge_text": data.cross_arc_bridge_text,
            "p1_v1_mapping": data.p1_v1_mapping,
        })
        if row is None:
            raise NotFoundError(f"Arc with number {data.arc_number} not found")
        return PositionResponse(**row)

    async def update_position(
        self, position_id: str, data: PositionUpdate
    ) -> PositionResponse:
        basic = await self._repo.get_position_basic(position_id)
        if basic is None:
            raise NotFoundError(f"Position '{position_id}' not found")
        if basic["status"] not in ("draft", "under_revision"):
            raise ConflictError(
                f"Position '{position_id}' is locked and cannot be edited"
            )
        update_data = data.model_dump(exclude_none=True)
        row = await self._repo.update_position(position_id, update_data)
        if row is None:
            raise NotFoundError(f"Position '{position_id}' not found")
        return PositionResponse(**row)

    async def lock_position(
        self, position_id: str, data: PositionLock
    ) -> PositionResponse:
        basic = await self._repo.get_position_basic(position_id)
        if basic is None:
            raise NotFoundError(f"Position '{position_id}' not found")
        if basic["status"] == "locked":
            raise ConflictError(
                f"Position '{position_id}' is already locked"
            )

        missing: list[str] = []
        if not basic.get("anti_position_text"):
            missing.append("anti_position_text")
        if not basic.get("cross_arc_bridge_text"):
            missing.append("cross_arc_bridge_text")
        if not basic.get("p1_v1_mapping"):
            missing.append("p1_v1_mapping")
        if missing:
            raise ValidationError(
                f"Cannot lock: missing required fields: {', '.join(missing)}"
            )

        row = await self._repo.lock_position(position_id, data.locked_by)
        if row is None:
            raise NotFoundError(f"Position '{position_id}' not found")
        return PositionResponse(**row)

    async def revise_position(
        self, position_id: str, data: PositionRevise
    ) -> PositionResponse:
        if data.trigger_type not in ("live_fire", "flash"):
            raise ValidationError(
                "trigger_type must be 'live_fire' or 'flash'"
            )
        basic = await self._repo.get_position_basic(position_id)
        if basic is None:
            raise NotFoundError(f"Position '{position_id}' not found")
        if basic["status"] != "locked":
            raise ConflictError(
                "Only locked positions can be revised"
            )
        new_id = str(uuid4())
        row = await self._repo.revise_position(position_id, new_id)
        if row is None:
            raise NotFoundError(f"Position '{position_id}' not found")
        return PositionResponse(**row)

    async def get_position_versions(
        self, position_id: str
    ) -> list[PositionVersionResponse]:
        rows = await self._repo.get_position_versions(position_id)
        if not rows:
            raise NotFoundError(f"Position '{position_id}' not found")
        return [PositionVersionResponse(**row) for row in rows]

    async def get_argument_map(self, position_id: str) -> ArgumentMapResponse:
        row = await self._repo.get_argument_map(position_id)
        if row is None:
            raise NotFoundError(f"Position {position_id} not found")
        return ArgumentMapResponse(
            position=PositionResponse(**row["position"]),
            supporting=[ArgumentSummary(**a) for a in row["supporting"]],
            challenging=[ArgumentSummary(**a) for a in row["challenging"]],
            steelman=[SteelmanItem(**s) for s in row["steelman"]],
            objection_pairs=[ObjectionPair(**o) for o in row["objection_pairs"]],
        )

    async def get_evidence_trail(
        self, position_id: str
    ) -> EvidenceTrailResponse:
        result = await self._repo.get_evidence_trail(position_id)
        if result is None:
            raise NotFoundError(f"Position {position_id} not found")

        evidence_items: list[EvidenceTrailItem] = []
        unsourced_count = 0
        bridge_bookmark_ids: set[str] = set()

        for ev in result["evidence"]:
            source_bookmark = None
            if ev.get("source_bookmark") is not None:
                sb = ev["source_bookmark"]
                source_bookmark = EvidenceTrailBookmark(**sb)
                arc_names = sb.get("arc_names", [])
                if len(arc_names) > 1:
                    bridge_bookmark_ids.add(sb["notion_id"])
            else:
                unsourced_count += 1

            evidence_items.append(
                EvidenceTrailItem(
                    id=ev["id"],
                    text=ev["text"],
                    type=ev["type"],
                    source_bookmark=source_bookmark,
                )
            )

        return EvidenceTrailResponse(
            position_id=result["position_id"],
            position_text=result["position_text"],
            evidence=evidence_items,
            unsourced_count=unsourced_count,
            bridge_bookmark_count=len(bridge_bookmark_ids),
        )

    async def get_changes_since_lock(
        self, position_id: str
    ) -> dict[str, object]:
        result = await self._repo.get_changes_since_lock(position_id)
        if result is None:
            raise NotFoundError(f"Position {position_id} not found")
        return {
            "new_evidence": [
                EvidenceChainItem(**e) for e in result["new_evidence"]
            ],
            "new_arguments": [
                ArgumentSummary(**a) for a in result["new_arguments"]
            ],
        }
