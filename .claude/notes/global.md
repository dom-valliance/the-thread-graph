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
