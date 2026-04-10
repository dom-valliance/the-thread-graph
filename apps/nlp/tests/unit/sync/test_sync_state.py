from __future__ import annotations

import json
from pathlib import Path

import pytest

from sync.sync_state import SyncState


@pytest.fixture()
def state_path(tmp_path: Path) -> Path:
    return tmp_path / "sync_state.json"


class TestSyncState:
    def test_get_last_sync_returns_none_when_not_set(
        self, state_path: Path,
    ) -> None:
        state = SyncState(state_path)
        assert state.get_last_sync("db-123") is None

    def test_update_last_sync_persists_to_disk(
        self, state_path: Path,
    ) -> None:
        state = SyncState(state_path)
        state.update_last_sync("db-123", "2026-04-01T12:00:00Z")

        assert state.get_last_sync("db-123") == "2026-04-01T12:00:00Z"

        raw = json.loads(state_path.read_text())
        assert raw["db-123"] == "2026-04-01T12:00:00Z"

    def test_update_preserves_other_entries(
        self, state_path: Path,
    ) -> None:
        state = SyncState(state_path)
        state.update_last_sync("db-aaa", "2026-03-01T00:00:00Z")
        state.update_last_sync("db-bbb", "2026-04-01T00:00:00Z")

        assert state.get_last_sync("db-aaa") == "2026-03-01T00:00:00Z"
        assert state.get_last_sync("db-bbb") == "2026-04-01T00:00:00Z"

    def test_clear_removes_entry(
        self, state_path: Path,
    ) -> None:
        state = SyncState(state_path)
        state.update_last_sync("db-123", "2026-04-01T12:00:00Z")
        state.clear("db-123")

        assert state.get_last_sync("db-123") is None

        raw = json.loads(state_path.read_text())
        assert "db-123" not in raw

    def test_clear_nonexistent_entry_does_not_raise(
        self, state_path: Path,
    ) -> None:
        state = SyncState(state_path)
        state.clear("nonexistent")

    def test_handles_missing_file(
        self, state_path: Path,
    ) -> None:
        assert not state_path.exists()
        state = SyncState(state_path)
        assert state.get_last_sync("anything") is None

    def test_handles_corrupt_file(
        self, state_path: Path,
    ) -> None:
        state_path.write_text("not valid json {{{")
        state = SyncState(state_path)
        assert state.get_last_sync("anything") is None

    def test_survives_reload_from_disk(
        self, state_path: Path,
    ) -> None:
        state1 = SyncState(state_path)
        state1.update_last_sync("db-123", "2026-04-01T12:00:00Z")

        state2 = SyncState(state_path)
        assert state2.get_last_sync("db-123") == "2026-04-01T12:00:00Z"
