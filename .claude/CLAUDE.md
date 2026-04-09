# Project: Valliance Graph

This file augments the global Valliance standards in `~/.claude/CLAUDE.md`. Do not repeat global rules here. Only project-specific conventions, stack details, and gotchas.

---

## Stack

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript 5.x, D3.js for graph visualisation
- **Middleware**: Python 3.12, FastAPI, Pydantic v2, uvicorn
- **Database**: Neo4j 5.x (Cypher), neo4j Python driver
- **NLP**: Python, OpenAI/Anthropic SDK for argument extraction
- **Infrastructure**: Azure (AKS), Terraform, Docker, GitHub Actions CI/CD
- **Package managers**: pnpm (frontend), uv (Python)
- **Monorepo layout**: Turborepo with `apps/` and `packages/` directories

## Architecture

Three-tier application: Next.js frontend communicates exclusively with the FastAPI middleware layer. The middleware owns all Neo4j access. No direct browser-to-database connections.

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Next.js UI  │────▶│  FastAPI API  │────▶│  Neo4j  │
│  (apps/web)  │◀────│  (apps/api)  │◀────│         │
└─────────────┘     └──────────────┘     └─────────┘
                           │
                    ┌──────┴───────┐
                    │  NLP Pipeline │
                    │  (apps/nlp)   │
                    └──────────────┘
```

## Project Conventions

### Directory Layout

```
valliance-graph/
├── apps/
│   ├── web/                 # Next.js frontend
│   │   ├── app/             # App Router pages and layouts
│   │   ├── components/      # React components
│   │   │   ├── ui/          # Generic UI primitives
│   │   │   └── graph/       # D3 visualisation components
│   │   ├── lib/             # Client utilities, API client, hooks
│   │   └── types/           # Shared TypeScript types
│   ├── api/                 # FastAPI middleware
│   │   ├── routers/         # Route modules (one per entity domain)
│   │   ├── services/        # Business logic layer
│   │   ├── repositories/    # Neo4j query layer (Cypher lives here)
│   │   ├── models/          # Pydantic models (request/response)
│   │   ├── schemas/         # Neo4j node/relationship schemas
│   │   └── core/            # Config, dependencies, middleware
│   └── nlp/                 # NLP enrichment pipeline
│       ├── extractors/      # Argument, entity, action item extractors
│       ├── processors/      # Transcript processing orchestration
│       └── prompts/         # LLM prompt templates (version controlled)
├── packages/
│   └── shared/              # Shared constants, enums, type definitions
├── infra/
│   ├── terraform/           # Azure infrastructure as code
│   │   ├── modules/         # Reusable TF modules (aks, neo4j, acr, etc.)
│   │   └── environments/    # Per-environment tfvars (dev, staging, prod)
│   ├── docker/              # Dockerfiles per service
│   └── k8s/                 # Kubernetes manifests (Helm charts or raw YAML)
├── scripts/                 # Dev tooling, seed scripts, migration helpers
├── .github/
│   └── workflows/           # CI/CD pipelines
└── .claude/                 # Claude Code project config
```

### API Conventions

- REST. All endpoints prefixed with `/api/v1/`.
- Response envelope: `{ "data": ..., "meta": { "count": n } }` for collections, `{ "data": ... }` for singles.
- Error envelope: `{ "error": { "code": "NOT_FOUND", "message": "..." } }` with appropriate HTTP status.
- Authentication: Azure AD JWT tokens validated in FastAPI middleware.
- Pagination: cursor-based via `?cursor=<id>&limit=25`.

### Neo4j Conventions

- All Cypher queries live in `apps/api/repositories/`. Never write Cypher in routers or services.
- Use parameterised queries exclusively. No string interpolation in Cypher.
- All write operations use MERGE keyed on Notion IDs for idempotence.
- Node labels are PascalCase singular: `Bookmark`, `Position`, `Arc`.
- Relationship types are UPPER_SNAKE_CASE: `TAGGED_WITH`, `EVIDENCES`, `LOCKED_IN`.
- Every node has a `created_at` and `updated_at` timestamp managed by the repository layer.

### Frontend Conventions

- All data fetching via server components or React Query (TanStack Query) for client components.
- D3 visualisations wrapped in React components with proper lifecycle management (useEffect for D3 bindings, cleanup on unmount).
- Tailwind CSS for layout and utility styling. No CSS modules.
- Components follow: `ComponentName/index.tsx` with co-located `ComponentName.test.tsx`.

### Python Conventions

- Type hints on all function signatures. No `Any` unless genuinely unavoidable.
- Async throughout the FastAPI layer. Sync only in NLP batch processing.
- Dependencies injected via FastAPI's `Depends()`. No global state.
- Pydantic models for all API boundaries. No raw dicts crossing service boundaries.

## Testing Strategy

### Frontend (apps/web)

- **Unit**: Vitest + React Testing Library. Test components in isolation.
- **Integration**: Test API client against mock server (MSW).
- **E2E**: Playwright for critical user journeys (arc explorer, topic galaxy navigation).
- **Visual regression**: Playwright screenshots for D3 visualisations.
- Coverage target: 80% line coverage on non-visualisation code.

### Middleware (apps/api)

- **Unit**: pytest. Test services with mocked repositories.
- **Integration**: pytest + testcontainers-neo4j. Test repositories against a real Neo4j instance.
- **API**: httpx AsyncClient against the FastAPI app with test database.
- Coverage target: 90% line coverage.
- Fixtures in `conftest.py` at each test directory level.

### NLP Pipeline (apps/nlp)

- **Unit**: pytest. Test extractors with fixture transcripts and expected outputs.
- **Evaluation**: LLM output quality checks against golden datasets (precision/recall on argument extraction).
- Coverage target: 85% on orchestration code. LLM call boundaries tested via mocks.

### Infrastructure

- **Terraform**: `terraform validate` and `terraform plan` in CI. No `apply` without manual approval.
- **Docker**: Build and scan images in CI. No critical/high CVEs in production images.
- **K8s**: Dry-run manifests with `kubectl apply --dry-run=client`.

## Environment Variables

```
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<from-secret>

# Notion
NOTION_API_KEY=<from-secret>
NOTION_BOOKMARKS_DB_ID=22d57534-6e48-8126-8580-000be39ca605
NOTION_SESSIONS_DB_ID=31857534-6e48-80a3-ada5-000b48b898c8

# Azure AD
AZURE_AD_TENANT_ID=<from-secret>
AZURE_AD_CLIENT_ID=<from-secret>

# LLM (for NLP pipeline)
ANTHROPIC_API_KEY=<from-secret>

# App
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Gotchas

- Neo4j MERGE operations must always include ON CREATE SET and ON MATCH SET. Bare MERGE without property handling creates empty nodes on first run.
- D3.js force simulations must be stopped on React component unmount or they leak timers and memory.
- FastAPI async endpoints must use the async neo4j driver (`neo4j.AsyncGraphDatabase`). Mixing sync driver calls in async handlers blocks the event loop.
- Notion API rate limit is 3 requests per second. The sync service must implement backoff and respect `Retry-After` headers.
- Terraform state is stored in Azure Blob Storage. Never run `terraform init` without the backend config or you get local state drift.
- Pydantic v2 uses `model_validate` not `parse_obj`. The v1 API is removed.
- Notion property types cannot be inferred from names. Always log `prop.get("type")` on first record before writing extraction logic. "Valliance Themes" is a relation, not a select. "* Theme" is the actual select. See `.claude/notes/notion-sync.md` for the full mapping.
- Sync transformer output field names must exactly match the target Pydantic model. Mismatches are silent (Pydantic uses defaults for missing fields, ignores extras).

## Memory Protocol

Claude maintains long-term memory in `.claude/notes/`. See the global CLAUDE.md for full protocol.

### Topic files expected to emerge

- `neo4j.md`: Cypher patterns, index management, driver quirks.
- `notion-sync.md`: API pagination, rate limiting, field mapping discoveries.
- `d3.md`: Force simulation tuning, React integration patterns.
- `infra.md`: Terraform state issues, AKS configuration, Docker build optimisations.
- `nlp.md`: Prompt engineering findings, extraction accuracy improvements.
