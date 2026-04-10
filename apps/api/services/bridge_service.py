from __future__ import annotations

from models.bridge import CrossArcBridgeResponse, UnconnectedPosition
from repositories.bridge_repository import BridgeRepository


class BridgeService:
    def __init__(self, repository: BridgeRepository) -> None:
        self._repo = repository

    async def list_bridges(self) -> list[CrossArcBridgeResponse]:
        rows = await self._repo.get_cross_arc_bridges()
        return [CrossArcBridgeResponse(**row) for row in rows]

    async def list_unconnected(self) -> list[UnconnectedPosition]:
        rows = await self._repo.get_unconnected_positions()
        return [UnconnectedPosition(**row) for row in rows]
