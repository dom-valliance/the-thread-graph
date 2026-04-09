# Module: Middleware (apps/api)

Python FastAPI service that sits between the Next.js frontend and Neo4j. Owns all graph queries, business logic, and external integrations.

---

## Technology

- Python 3.12
- FastAPI 0.110+
- Pydantic v2 (all models, validation, serialisation)
- neo4j async driver (neo4j-driver 5.x)
- uvicorn (ASGI server)
- uv (package manager, virtualenv)
- httpx (async HTTP client for Notion API)

## Responsibilities

- Expose REST API consumed by the frontend.
- Translate API requests into parameterised Cypher queries.
- Enforce authentication (validate Azure AD JWT tokens).
- Implement response envelope, pagination, error formatting.
- Provide endpoints for the NLP pipeline to write enrichment results.
- Serve as the single point of access to Neo4j.

## Directory Structure

```
apps/api/
├── main.py                     # FastAPI app factory, middleware, lifespan
├── routers/
│   ├── arcs.py                 # /api/v1/arcs
│   ├── bookmarks.py            # /api/v1/bookmarks
│   ├── positions.py            # /api/v1/positions
│   ├── sessions.py             # /api/v1/sessions
│   ├── topics.py               # /api/v1/topics
│   ├── arguments.py            # /api/v1/arguments
│   ├── evidence.py             # /api/v1/evidence
│   ├── players.py              # /api/v1/players
│   ├── objections.py           # /api/v1/objections
│   ├── search.py               # /api/v1/search (cross-entity)
│   └── health.py               # /api/v1/health
├── services/
│   ├── arc_service.py
│   ├── bookmark_service.py
│   ├── position_service.py
│   ├── session_service.py
│   ├── search_service.py
│   ├── argument_service.py
│   └── evidence_service.py
├── repositories/
│   ├── base.py                 # Base repository with Neo4j session management
│   ├── arc_repository.py       # Arc CRUD + bridge queries
│   ├── bookmark_repository.py  # Bookmark CRUD + relationship queries
│   ├── position_repository.py  # Position + anti-position + versioning queries
│   ├── session_repository.py   # Session + argument + action item queries
│   ├── topic_repository.py     # Topic + co-occurrence queries
│   ├── argument_repository.py  # Argument traversal queries
│   ├── evidence_repository.py  # Evidence vault queries
│   └── search_repository.py    # Cross-entity full-text search
├── models/
│   ├── common.py               # ApiResponse envelope, PaginationMeta, ErrorResponse
│   ├── arc.py                  # ArcResponse, ArcDetail, CrossArcBridgeResponse
│   ├── bookmark.py             # BookmarkResponse, BookmarkCreate
│   ├── position.py             # PositionResponse, PositionDetail, AntiPositionResponse
│   ├── session.py              # SessionResponse, SessionDetail
│   ├── topic.py                # TopicResponse, TopicCoOccurrence
│   ├── argument.py             # ArgumentResponse, ArgumentMapResponse
│   ├── evidence.py             # EvidenceResponse
│   └── search.py               # SearchResult, SearchQuery
├── schemas/
│   ├── nodes.py                # Neo4j node property definitions (mirror of architecture brief Section 1)
│   └── relationships.py        # Relationship type constants and property definitions
├── core/
│   ├── config.py               # Settings from environment variables (Pydantic BaseSettings)
│   ├── database.py             # Neo4j async driver lifecycle (startup/shutdown)
│   ├── auth.py                 # Azure AD JWT validation middleware
│   ├── dependencies.py         # FastAPI Depends() factories
│   ├── exceptions.py           # Custom exception classes + handlers
│   └── middleware.py           # CORS, request logging, timing
├── tests/
│   ├── conftest.py             # Shared fixtures: test client, mock Neo4j driver
│   ├── unit/
│   │   ├── services/           # Service tests with mocked repositories
│   │   └── models/             # Pydantic model validation tests
│   ├── integration/
│   │   ├── conftest.py         # testcontainers Neo4j fixtures
│   │   └── repositories/      # Repository tests against real Neo4j
│   └── api/
│       ├── conftest.py         # httpx AsyncClient fixture
│       └── test_*.py           # Endpoint tests
├── pyproject.toml
└── Dockerfile
```

## Layered Architecture

```
Router  →  Service  →  Repository  →  Neo4j
  │           │            │
  │           │            └── Cypher queries (parameterised)
  │           └── Business logic, validation, transformation
  └── HTTP handling, auth, response envelope
```

Strict layer separation. Routers never import repositories. Services never construct Cypher. Repositories never raise HTTP exceptions.

## API Endpoints

### Arcs

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/arcs | List all arcs with position counts |
| GET | /api/v1/arcs/{id} | Arc detail with positions, bridges, steelman arguments |
| GET | /api/v1/arcs/{id}/positions | Positions for this arc with evidence chains |
| GET | /api/v1/arcs/bridges | All cross-arc bridges |

### Bookmarks

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/bookmarks | Paginated bookmarks with filters (topic, theme, edge/foundational) |
| GET | /api/v1/bookmarks/{id} | Bookmark detail with all relationships |
| GET | /api/v1/bookmarks/high-connectivity | Bookmarks influencing multiple arcs |

### Positions

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/positions | List positions with filters (arc, status, proposition) |
| GET | /api/v1/positions/{id} | Position detail with evidence chain |
| GET | /api/v1/positions/{id}/arguments | Argument map (for/against/steelman) |
| GET | /api/v1/positions/{id}/changes-since-lock | Evidence and arguments added after lock date |

### Sessions

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/sessions | Session timeline with filters (arc, person, date range) |
| GET | /api/v1/sessions/{id} | Session detail with arguments, action items, referenced bookmarks |

### Topics

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/topics | Topics with co-occurrence data |
| GET | /api/v1/topics/{id}/bookmarks | Bookmarks tagged with this topic |
| GET | /api/v1/topics/cross-arc | Topics appearing in 3+ arcs |

### Search

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/search?q=... | Cross-entity full-text search |

### Enrichment (internal, for NLP pipeline)

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/enrichment/arguments | Batch create arguments from NLP extraction |
| POST | /api/v1/enrichment/action-items | Batch create action items |
| POST | /api/v1/enrichment/evidence | Create evidence nodes |
| POST | /api/v1/sync/bookmarks | Upsert bookmarks from Notion sync |
| POST | /api/v1/sync/sessions | Upsert sessions from Notion sync |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | App health including Neo4j connectivity |

## Response Envelope

```python
class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: dict | None = None

class PaginatedResponse(ApiResponse[list[T]], Generic[T]):
    meta: PaginationMeta

class PaginationMeta(BaseModel):
    count: int
    cursor: str | None = None
    has_more: bool

class ErrorResponse(BaseModel):
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: str
    message: str
```

## Repository Pattern

```python
class BaseRepository:
    def __init__(self, driver: AsyncDriver):
        self._driver = driver

    async def _read(self, query: str, params: dict) -> list[Record]:
        async with self._driver.session() as session:
            result = await session.run(query, params)
            return [record async for record in result]

    async def _write(self, query: str, params: dict) -> ResultSummary:
        async with self._driver.session() as session:
            result = await session.run(query, params)
            return await result.consume()
```

All queries parameterised. All writes use MERGE with ON CREATE/ON MATCH SET.

## Testing

- **Unit**: pytest. Services tested with mocked repository return values. Pydantic model validation tested with valid and invalid payloads.
- **Integration**: testcontainers-neo4j spins up a real Neo4j instance. Repositories tested against it with seed data. Fixtures in `tests/integration/conftest.py`.
- **API**: httpx AsyncClient against the FastAPI app. Auth bypassed via dependency override. Neo4j mocked at the repository level.
- **Coverage target**: 90% line coverage.

## Build and Dev

```bash
# Setup
cd apps/api
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Development
uvicorn main:app --reload --port 8000

# Test
pytest -v                           # All tests
pytest -v -m "not integration"      # Unit only
pytest -v -m integration            # Integration only (requires Docker)

# Lint
ruff check .
mypy .
```
