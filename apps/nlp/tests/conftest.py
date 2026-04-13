from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure the nlp package root is on sys.path for test imports.
NLP_ROOT = Path(__file__).parent.parent
if str(NLP_ROOT) not in sys.path:
    sys.path.insert(0, str(NLP_ROOT))

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_transcript() -> str:
    return (FIXTURES_DIR / "sample_transcript_1.txt").read_text()


@pytest.fixture()
def expected_arguments() -> list[dict[str, object]]:
    return json.loads((FIXTURES_DIR / "expected_arguments_1.json").read_text())
