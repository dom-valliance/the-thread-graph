# Module: NLP Enrichment Pipeline (apps/nlp)

Python service that extracts structured entities from session transcripts and notes, feeding the graph with arguments, action items, evidence, and entity references.

---

## Technology

- Python 3.12
- Anthropic SDK (Claude for extraction)
- httpx (async HTTP client to call FastAPI enrichment endpoints)
- Pydantic v2 (structured output parsing)
- uv (package manager)

## Responsibilities

- Poll for new/updated sessions that have not been enriched.
- Extract arguments with speaker attribution, sentiment, and strength.
- Extract action items with assignee and due date.
- Identify evidence statements that support or challenge existing positions.
- Recognise entity mentions (People, Topics, Players) and link to existing graph nodes.
- Submit extracted data to the FastAPI enrichment endpoints.
- Track enrichment status to avoid reprocessing.

## Directory Structure

```
apps/nlp/
├── main.py                     # Entry point: poll, process, submit
├── extractors/
│   ├── base.py                 # Base extractor interface
│   ├── argument_extractor.py   # Extract arguments from transcript
│   ├── action_item_extractor.py # Extract action items
│   ├── evidence_extractor.py   # Identify evidence for positions
│   └── entity_extractor.py     # NER for people, topics, players
├── processors/
│   ├── transcript_processor.py # Orchestrates extraction pipeline per session
│   └── batch_processor.py      # Handles multiple sessions, rate limiting
├── prompts/
│   ├── argument_extraction.txt # LLM prompt template for arguments
│   ├── action_item_extraction.txt
│   ├── evidence_identification.txt
│   └── entity_recognition.txt
├── models/
│   ├── extraction.py           # Pydantic models for extraction results
│   └── session.py              # Session input model
├── client/
│   └── api_client.py           # Typed client for FastAPI enrichment endpoints
├── tests/
│   ├── conftest.py
│   ├── fixtures/               # Sample transcripts and expected outputs
│   │   ├── sample_transcript_1.txt
│   │   ├── expected_arguments_1.json
│   │   ├── sample_transcript_2.txt
│   │   └── expected_arguments_2.json
│   ├── unit/
│   │   ├── test_argument_extractor.py
│   │   ├── test_action_item_extractor.py
│   │   ├── test_evidence_extractor.py
│   │   └── test_entity_extractor.py
│   └── evaluation/
│       └── test_extraction_quality.py  # Precision/recall against golden dataset
├── pyproject.toml
└── Dockerfile
```

## Extraction Pipeline

```
Session transcript
    │
    ├──▶ Argument Extractor
    │       → arguments with speaker, sentiment, strength, timestamp
    │
    ├──▶ Action Item Extractor
    │       → tasks with assignee, due date
    │
    ├──▶ Evidence Extractor
    │       → evidence linked to position IDs
    │
    └──▶ Entity Extractor
            → people, topics, players mentioned
    │
    ▼
Transcript Processor (merges, deduplicates, validates)
    │
    ▼
API Client (submits to FastAPI enrichment endpoints)
```

## Extractor Design

Each extractor follows the same pattern:

```python
class BaseExtractor(ABC):
    def __init__(self, client: anthropic.AsyncAnthropic):
        self._client = client

    @abstractmethod
    async def extract(self, transcript: str, context: ExtractionContext) -> list[BaseModel]:
        """Extract entities from transcript text."""
        ...

    def _build_prompt(self, transcript: str, context: ExtractionContext) -> str:
        """Load prompt template and inject transcript and context."""
        ...
```

### ExtractionContext

Passed to every extractor to ground extraction against existing graph state:

```python
class ExtractionContext(BaseModel):
    session_id: str
    arc_name: str
    existing_positions: list[PositionSummary]    # So evidence extractor can link
    existing_people: list[PersonSummary]          # So entity extractor can match
    existing_topics: list[str]                    # So entity extractor can match
    existing_players: list[str]                   # So entity extractor can match
```

The pipeline fetches this context from the API before running extractors.

## Prompt Engineering

Prompts are version-controlled in `prompts/`. Each prompt:

1. Defines the extraction task precisely.
2. Provides the output schema (JSON) that Pydantic will validate.
3. Includes 2-3 few-shot examples drawn from real Valliance sessions.
4. Specifies what to exclude (off-topic remarks, logistics, pleasantries).

Prompts use Anthropic's structured output / tool use to enforce JSON schema compliance.

## Quality Assurance

### Golden Dataset

A set of 10+ manually annotated session transcripts stored in `tests/fixtures/`. Each has:
- Raw transcript
- Expected arguments (hand-labelled)
- Expected action items (hand-labelled)
- Expected evidence links (hand-labelled)

### Evaluation Metrics

```python
def evaluate_extraction(predicted: list, expected: list) -> dict:
    """
    Returns precision, recall, F1 for extraction quality.
    Match is fuzzy: predicted argument must overlap >70% with expected.
    """
```

Target: 80% F1 on argument extraction, 90% on action items (more structured, easier).

### Unit Tests

- Mock the Anthropic client.
- Feed fixture transcripts through extractors.
- Assert output matches expected Pydantic models.
- Test edge cases: empty transcripts, single-speaker sessions, sessions with no action items.

## Scheduling

- Runs as a Kubernetes CronJob, hourly.
- On each run: query API for sessions with `enrichment_status != "complete"`.
- Process each session through the full pipeline.
- On success: mark session enrichment as complete via API.
- On failure: log error, leave session for retry on next run. Alert after 3 consecutive failures.

## Rate Limiting

- Anthropic API: respect rate limits, implement exponential backoff.
- FastAPI enrichment endpoints: batch submissions (50 arguments per request max).
- Process at most 5 sessions per run to avoid timeout.

## Build and Dev

```bash
# Setup
cd apps/nlp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run locally (processes one session)
python main.py --session-id <id>

# Run batch (all unprocessed)
python main.py --batch

# Test
pytest -v
pytest -v tests/evaluation/  # Quality evaluation

# Lint
ruff check .
mypy .
```
