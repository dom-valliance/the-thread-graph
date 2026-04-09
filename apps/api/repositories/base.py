from __future__ import annotations

from neo4j import AsyncDriver, Record, ResultSummary
from neo4j.time import Date, DateTime, Duration, Time


def _serialise_value(value: object) -> object:
    """Convert Neo4j temporal types to ISO 8601 strings."""
    if isinstance(value, (DateTime, Date, Time)):
        return value.iso_format()
    if isinstance(value, Duration):
        return str(value)
    if isinstance(value, dict):
        return {k: _serialise_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialise_value(v) for v in value]
    return value


def serialise_record(record_map: dict[str, object]) -> dict[str, object]:
    """Serialise a Neo4j record map, converting temporal types to strings."""
    return {k: _serialise_value(v) for k, v in record_map.items()}


class BaseRepository:
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def _read(
        self, query: str, params: dict[str, object] | None = None
    ) -> list[Record]:
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            return [record async for record in result]

    async def _write(
        self, query: str, params: dict[str, object] | None = None
    ) -> ResultSummary:
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            return await result.consume()

    async def _write_and_return(
        self, query: str, params: dict[str, object] | None = None
    ) -> list[Record]:
        """Execute a write query and return the result records.

        Uses a managed write transaction so that writes are routed
        correctly on causal clusters.
        """
        async def _tx_fn(tx: object) -> list[Record]:
            result = await tx.run(query, params or {})  # type: ignore[union-attr]
            return [record async for record in result]

        async with self._driver.session() as session:
            return await session.execute_write(_tx_fn)
