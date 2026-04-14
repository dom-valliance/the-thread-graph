# Project: Valliance Graph

This file augments the global Valliance standards in `~/.claude/CLAUDE.md`. Do not repeat global rules here. Only project-specific conventions, stack details, and gotchas.

---

## Stack

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript 5.x, Tailwind CSS v4, D3.js for graph visualisation, @valliance-ai/design-system v0.2.x
- **Middleware**: Python 3.12, FastAPI, Pydantic v2, uvicorn, LangGraph + langchain-anthropic
- **Database**: Neo4j 5.x (Cypher), neo4j Python driver
- **NLP**: Python, LangGraph StateGraph agents (Claude via langchain-anthropic) for argument extraction, evidence extraction, entity extraction, action item extraction, theme classification, and thread prep generation
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
│   │   │   ├── ui/          # Design system re-export adapters (Button, Card, SearchBar, etc.)
│   │   │   └── graph/       # D3 visualisation components (use lib/graph-colours.ts)
│   │   ├── lib/             # Client utilities, API client, hooks, graph-colours.ts
│   │   └── types/           # Shared TypeScript types
│   ├── api/                 # FastAPI middleware
│   │   ├── routers/         # Route modules (one per entity domain)
│   │   ├── services/        # Business logic layer
│   │   ├── repositories/    # Neo4j query layer (Cypher lives here)
│   │   ├── models/          # Pydantic models (request/response)
│   │   ├── schemas/         # Neo4j node/relationship schemas
│   │   └── core/            # Config, dependencies, middleware
│   └── nlp/                 # NLP enrichment pipeline
│       ├── graphs/          # LangGraph StateGraph definitions (one per extraction type)
│       ├── extractors/      # Thin wrappers delegating to graphs/ (argument, entity, action item, evidence)
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
- Tailwind CSS v4 for styling. Configuration is CSS-based (no `tailwind.config.ts`). The DS globals.css (`@valliance-ai/design-system/styles/globals.css`) is imported in `app/globals.css` and provides all tokens, theme variables, and the `@import "tailwindcss"` directive. No CSS modules.
- UI primitives (Button, Card, Spinner, Input) re-exported from `@valliance-ai/design-system` via adapter components in `components/ui/`. Do not use raw Tailwind for base components; use the design system.
- Layout components (Sidebar, Header) use design system primitives (`NavItem`, `PageHeader`).
- D3 graph colours must be imported from `lib/graph-colours.ts`. Never hardcode hex colour values in graph components.
- Components follow: `ComponentName/index.tsx` with co-located `ComponentName.test.tsx`.

### LangGraph Conventions

- All LLM workloads use LangGraph `StateGraph` definitions in `apps/nlp/graphs/` or `apps/api/graphs/`.
- Each graph has a typed `State` (TypedDict), prompt-building node(s), and an extraction/generation node.
- LLM instances created via `graphs/llm.py:get_llm()`. Never instantiate `ChatAnthropic` directly.
- Tool schemas are Pydantic models in `graphs/tool_schemas.py`, bound via `ChatAnthropic.bind_tools()`.
- Extractors in `apps/nlp/extractors/` are thin wrappers that call `graph.ainvoke()`. Business logic lives in graph nodes.
- Tests mock the compiled graph's `ainvoke` method, not the LLM directly.

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

- **Unit**: pytest. Test extractors by mocking the compiled LangGraph `ainvoke` method (not the LLM directly). Use `@patch("extractors.<name>_extractor.<name>_graph")`.
- **Evaluation**: LLM output quality checks against golden datasets (precision/recall on argument extraction).
- Coverage target: 85% on orchestration code. Graph boundaries tested via mocks on `ainvoke`.

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
- When creating a paginated or filtered variant of an existing Cypher query, diff the RETURN clause field-by-field against the original. Missing fields cause silent `undefined` values that crash the frontend. Use optional chaining (`?.`) on all array property access in components consuming API data.
- Theme and Arc are distinct concepts. Theme (`HAS_THEME`) is a Notion classification label. Arc (`BELONGS_TO_ARC`) is a structural Thread curriculum category. When a feature needs arc alignment, use `BELONGS_TO_ARC`, not `HAS_THEME`.
- FastAPI `status_code=204` endpoints must include `response_model=None` in the decorator, otherwise FastAPI raises "Status code 204 must not have a response body". When fixing any pattern-based issue, grep the entire codebase for the same pattern and fix all occurrences in one pass.
- LangGraph `tool_calls` format: `AIMessage.tool_calls` returns `list[dict]` with keys `name`, `args`, `id`. The `name` matches the Pydantic model class name (e.g. `ArgumentToolInput`), not the original Anthropic tool name. Always filter by class name, not the old tool name.
- D3 graph components operate outside React's render cycle. If design system tokens are CSS custom properties, they must be resolved to raw hex/rgb via `getComputedStyle` before passing to D3 `.style()` or `.attr()` calls. The centralised `lib/graph-colours.ts` handles this.
- The `@valliance-ai/design-system` package is hosted on GitHub Packages. The `.npmrc` at repo root configures the `@valliance-ai` scope. A valid `GITHUB_TOKEN` environment variable is required for `pnpm install`.
- The design system requires Tailwind v4, `@tailwindcss/postcss`, `tw-animate-css`, `shadcn`, `next-themes`, and `recharts` as peer/transitive dependencies. PostCSS config uses `@tailwindcss/postcss` (not `tailwindcss`). There is no `tailwind.config.ts`; all config is in CSS.
- When migrating LLM workloads to LangGraph, always update the corresponding tests to mock at the graph level (`graph.ainvoke`), not at the old Anthropic SDK level. Tests that inspect prompt content should be rewritten to verify the correct context/state is passed to the graph.
- Never MERGE a Neo4j node by a free-form Notion tag string without normalising first. Notion multi-select / select values drift in spelling ("Consulting Craft" vs "The Consulting Craft", "Palantir/Ontology" vs "Palantir / Ontology") and each variant creates a duplicate node. Normalise via an explicit alias map in the transformer; for closed sets like the six Arcs, the map is also the canonical source of truth that `scripts/seed.py` must match.
- Date values written to Neo4j must be cast to the Date type at MERGE time (`date(datetime(item.date_added))` for ISO strings, `date($s)` for plain `YYYY-MM-DD`). Storing dates as plain strings disables date arithmetic (`b.date_added >= date() - duration(...)`) and breaks indexes — the failure mode is silent (queries return zero rows). When extracting from Notion, switch on `prop.get("type")` because `date`, `created_time`, and `last_edited_time` payloads live under different keys.
- Inside multi-row Cypher writes (UNWIND or per-row WITH chains), never use bare `MATCH` to look up a related entity that may not exist. A failed `MATCH` silently drops the row from the rest of the pipeline, leaving the primary write half-finished. Use `OPTIONAL MATCH` plus a `FOREACH (_ IN CASE WHEN x IS NOT NULL THEN [1] ELSE [] END | ...)` guard for the dependent relationship.

## Memory Protocol

Claude maintains long-term memory in `.claude/notes/`. See the global CLAUDE.md for full protocol.

### Topic files expected to emerge

- `neo4j.md`: Cypher patterns, index management, driver quirks.
- `notion-sync.md`: API pagination, rate limiting, field mapping discoveries.
- `d3.md`: Force simulation tuning, React integration patterns.
- `infra.md`: Terraform state issues, AKS configuration, Docker build optimisations.
- `nlp.md`: Prompt engineering findings, extraction accuracy improvements.
- `langgraph.md`: LangGraph patterns, tool schema conventions, state management.
- `design-system.md`: @valliance-ai/design-system integration patterns, token usage.
