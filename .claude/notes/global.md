# Project Learnings

### [2026-04-08] Docker Compose: Next.js needs two API URL env vars

**Context**: Web container server components could not reach the API at `localhost:8000` because inside Docker that resolves to the container itself.
**Correction**: The web service needs both `API_URL=http://api:8000/api/v1` (server-side, Docker DNS) and `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` (client-side, browser). The API client reads `API_URL` first, falling back to `NEXT_PUBLIC_API_URL`.
**Rule**: When a Next.js app runs in Docker, always provide a separate server-side URL using Docker service names. Never assume `localhost` works from inside a container.
**Applies to**: docker-compose.yml, apps/web/lib/api-client.ts

### [2026-04-08] Dockerfiles need .dockerignore to avoid bloated build contexts

**Context**: API Docker build transferred 126MB because `.venv/` and `__pycache__/` were included. Web build similarly pulled in `node_modules/` and `.next/`.
**Correction**: Added `.dockerignore` files excluding `.venv`, `__pycache__`, `.pytest_cache`, `node_modules`, `.next`, `.turbo`.
**Rule**: Always create `.dockerignore` alongside any Dockerfile. Exclude venvs, caches, build output, and dependency directories.
**Applies to**: apps/api/.dockerignore, apps/web/.dockerignore

### [2026-04-08] pnpm Dockerfile must handle missing lockfile

**Context**: Web Dockerfile used `pnpm install --frozen-lockfile` but no `pnpm-lock.yaml` existed yet, causing the build to fail.
**Correction**: Changed to `--no-frozen-lockfile`. Production Dockerfiles in `infra/docker/` use the wildcard `pnpm-lock.yaml*` COPY pattern and fall back gracefully.
**Rule**: Dev Dockerfiles should use `--no-frozen-lockfile`. Production Dockerfiles should require a lockfile and fail explicitly if absent.
**Applies to**: apps/web/Dockerfile, infra/docker/web.Dockerfile

### [2026-04-08] Do not assume CLI tools are installed on the host

**Context**: README instructed users to run `cypher-shell -f scripts/init-schema.cypher` directly, but cypher-shell is not commonly installed outside the Neo4j container.
**Correction**: README should prefer `docker compose exec neo4j cypher-shell ...` or `docker exec` commands. Only mention bare `cypher-shell` as a secondary option.
**Rule**: When writing documentation, always provide the Docker exec variant first for any tool that ships inside a container (cypher-shell, psql, redis-cli, etc.). Do not assume host installation.
**Applies to**: README.md, scripts documentation

### [2026-04-10] Theme and Arc are distinct concepts — do not conflate them

**Context**: The `list_topics` Cypher query derived `primary_theme` via `HAS_THEME` (Notion's "* Theme" select field) instead of `primary_arc` via `BELONGS_TO_ARC`. The frontend `Topic` type expected `primary_arc`, so the field was always null and topics showed "No arc" in the TopicGalaxy.
**Correction**: Changed the query to traverse `BELONGS_TO_ARC` and renamed the model field from `primary_theme` to `primary_arc`.
**Rule**: Theme (`HAS_THEME`) is a Notion classification label (e.g. "AI Governance"). Arc (`BELONGS_TO_ARC`) is a structural curriculum category (e.g. "Agentic Engineering"). They are different node types with different relationships. When a feature needs arc alignment, always use `BELONGS_TO_ARC`, never `HAS_THEME`.
**Applies to**: apps/api/repositories/topic_repository.py, apps/api/models/topic.py, any query needing arc membership

### [2026-04-10] Paginated query variants must return every field the original returns

**Context**: Created `get_arc_bookmarks_paginated` as a SKIP/LIMIT variant of `get_arc_bookmarks`. The original collects `topic_names` but never collected `arc_bucket_names`. The paginated version also omitted it. The frontend `BookmarkDetailPanel` accessed `bookmark.arc_bucket_names.length` without optional chaining, causing a runtime crash.
**Correction**: (a) Added `?.` guards on all array property access in frontend components. (b) Added the missing `OPTIONAL MATCH (b)-[:BELONGS_TO_ARC]->(arc:Arc)` clause to the paginated query to collect `arc_bucket_names`.
**Rule**: When creating a paginated or filtered variant of an existing Cypher query, diff the RETURN clause field-by-field against the original. Every field the original returns must appear in the variant. On the frontend, always use optional chaining (`?.`) when accessing array properties on API response objects — the shape may differ between endpoints.
**Applies to**: apps/api/repositories/, apps/web/components/

### [2026-04-08] Neo4j map projections with aggregation need a preceding WITH clause

**Context**: Cypher query `RETURN a { .number, position_count: count(p) } AS arc ORDER BY a.number` failed with two errors: (1) aggregation mixed with property access in map projection, and (2) ORDER BY referencing the original variable after aggregation.
**Correction**: Separate aggregation into a `WITH a, count(p) AS position_count` clause, then build the map projection from both, and `ORDER BY arc.number` (the alias, not the node variable).
**Rule**: In Neo4j 5, never mix aggregation functions directly into map projections. Always use a preceding WITH clause for the aggregation, then project the result. ORDER BY must reference the RETURN alias, not the original node variable.
**Applies to**: apps/api/repositories/

### [2026-04-08] Neo4j driver returns temporal types, not strings

**Context**: Pydantic models expected `str` for `created_at`/`updated_at`, but the Neo4j driver returns `neo4j.time.DateTime` objects, causing serialisation failures.
**Correction**: Added `serialise_record()` helper in `repositories/base.py` that converts `DateTime`, `Date`, `Time`, and `Duration` to ISO 8601 strings. All repository methods must apply it before returning dicts.
**Rule**: Every repository method that returns dicts from Neo4j records must apply `serialise_record()` to convert temporal types. Never pass raw Neo4j records to Pydantic models.
**Applies to**: apps/api/repositories/

### [2026-04-10] Fix patterns across all files, not just the first occurrence

**Context**: FastAPI `status_code=204` endpoints failed with "must not have a response body". Claude fixed it in `evidence.py` but did not grep for the same pattern in other router files. The user had to restart, hit the identical error in `objections.py`, and report it again.
**Correction**: After fixing `evidence.py`, should have immediately grepped for `status_code=204` across all routers and applied the fix (`response_model=None`) everywhere.
**Rule**: When fixing a pattern-based bug, always search the entire codebase for the same pattern before declaring the fix complete. One occurrence almost always means more.
**Applies to**: global

### [2026-04-11] LangGraph tool_calls use Pydantic class names, not Anthropic tool names

**Context**: Migrating extractors from direct Anthropic SDK to LangGraph. The old code filtered tool_use blocks by the Anthropic tool name (e.g. `store_arguments`). LangGraph's `AIMessage.tool_calls` returns tool calls where `name` is the Pydantic model class name (e.g. `ArgumentToolInput`), not the original Anthropic tool name.
**Correction**: Updated all graph extract nodes to filter by the Pydantic class name.
**Rule**: When using `ChatAnthropic.bind_tools()` with Pydantic models, `AIMessage.tool_calls[n]["name"]` matches the class name, not any `description` or original tool name. Always filter by the Pydantic model class name.
**Applies to**: apps/nlp/graphs/, apps/api/graphs/

### [2026-04-11] LangGraph migration requires test updates at the mock boundary

**Context**: After migrating extractors to LangGraph, all 27 extractor tests failed because they mocked `anthropic.AsyncAnthropic.messages.create`, but extractors no longer use that interface.
**Correction**: Rewrote tests to mock the compiled graph's `ainvoke` method using `@patch("extractors.<name>_extractor.<name>_graph")`. Tests that inspected prompt strings were converted to verify the correct context/state is passed to the graph.
**Rule**: When migrating LLM integrations to a new framework, always update the test mocking boundary in the same pass. Mock the new interface (graph `ainvoke`), not the old one (SDK client). Prompt-content tests become state-passing tests.
**Applies to**: apps/nlp/tests/

### [2026-04-11] Design system re-export adapter pattern preserves import paths

**Context**: Integrating `@valliance-ai/design-system` into the frontend. Components across the codebase import from `@/components/ui/Button`, `@/components/ui/Card`, etc.
**Correction**: Used a re-export adapter pattern: existing component files at their original paths now re-export from the design system, mapping props where needed. Zero import path changes required across consumers.
**Rule**: When adopting a design system, use re-export adapters at existing component paths to avoid a mass import refactor. Map any prop differences in the adapter.
**Applies to**: apps/web/components/ui/

### [2026-04-11] @valliance-ai/design-system requires Tailwind v4 and specific peer dependencies

**Context**: Integrated `@valliance-ai/design-system@0.2.0` assuming Tailwind v3 compatibility. The DS globals.css uses `@import "tailwindcss"` (v4 syntax), `@import "tw-animate-css"`, and `@import "shadcn/tailwind.css"`. PostCSS with the v3 `tailwindcss` plugin could not process these.
**Correction**: Upgraded to Tailwind v4 (`tailwindcss@4`, `@tailwindcss/postcss@4`). Installed `tw-animate-css`, `shadcn`, `next-themes`, `recharts` as additional dependencies. Removed `tailwind.config.ts` (v4 is CSS-configured). Changed PostCSS plugin from `tailwindcss` to `@tailwindcss/postcss`. Changed `globals.css` to just `@import '@valliance-ai/design-system/styles/globals.css'`.
**Rule**: Always check the DS package.json `peerDependencies` and its CSS `@import` statements before integrating. The DS exports only `.` and `./styles/globals.css` -- no `./tailwind-preset`. It requires Tailwind v4. Do not assume Tailwind v3 compatibility.
**Applies to**: apps/web/package.json, apps/web/postcss.config.js, apps/web/app/globals.css

### [2026-04-11] D3 graph colours must be centralised, not scattered

**Context**: 6 D3 graph components each defined their own hex colour constants (~50 hardcoded values total). This made design system token adoption painful and inconsistent.
**Correction**: Created `lib/graph-colours.ts` as a single source of truth exporting semantic colour constants, an arc palette, and neutral scale values. All 6 graph components now import from this module.
**Rule**: Never hardcode hex colours in D3 graph components. Import from `lib/graph-colours.ts`. When adding a new graph component, use the existing palette and neutral constants.
**Applies to**: apps/web/components/graph/, apps/web/lib/graph-colours.ts
