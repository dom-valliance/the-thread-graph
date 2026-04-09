from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = Path(__file__).parent.parent / "sync_state.json"


class SyncState:
    """Persists the last sync timestamp per Notion database ID to a local JSON file."""

    def __init__(self, state_path: Path = DEFAULT_STATE_PATH) -> None:
        self._state_path = state_path
        self._state = self._load()

    def _load(self) -> dict[str, str]:
        if not self._state_path.exists():
            return {}
        try:
            return json.loads(self._state_path.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("Corrupt or unreadable sync state file. Starting fresh.")
            return {}

    def _save(self) -> None:
        self._state_path.write_text(json.dumps(self._state, indent=2) + "\n")

    def get_last_sync(self, db_id: str) -> str | None:
        return self._state.get(db_id)

    def update_last_sync(self, db_id: str, timestamp: str) -> None:
        self._state[db_id] = timestamp
        self._save()

    def clear(self, db_id: str) -> None:
        self._state.pop(db_id, None)
        self._save()
