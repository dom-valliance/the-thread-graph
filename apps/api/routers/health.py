from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(driver: AsyncDriver = Depends(get_driver)) -> dict:
    """Health check including Neo4j connectivity."""
    try:
        async with driver.session() as session:
            result = await session.run("RETURN 1 AS ok")
            await result.consume()
        neo4j_status = "connected"
    except Exception:
        neo4j_status = "disconnected"

    return {
        "data": {
            "status": "ok" if neo4j_status == "connected" else "degraded",
            "neo4j": neo4j_status,
        }
    }
