# Valliance Graph

Knowledge graph and operational platform for the Valliance Thread, a continuous 12-week learning curriculum. Ingests bookmarks and session recordings from Notion, extracts arguments and evidence using NLP, manages the cycle lifecycle (scheduling, session capture, lock workflow, evidence tracking, content pipeline), and visualises the resulting graph through interactive D3 views.

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

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), React 18, TypeScript 5, D3.js 7, TanStack Query 5, Tailwind CSS v4, @valliance-ai/design-system v0.2.x |
| Middleware | Python 3.12, FastAPI, Pydantic v2, async neo4j driver, LangGraph + LangChain (Anthropic) |
| Database | Neo4j 5.x |
| NLP | Python, LangGraph agents (Claude via langchain-anthropic) for argument extraction and thread prep generation |
| Sync | Notion API via httpx with rate limiting |
| Infrastructure | Azure (AKS), Terraform, Docker, Kustomize, GitHub Actions |
| Package managers | pnpm (frontend), uv (Python) |
| Monorepo | Turborepo |

## Repository Layout

```
├── apps/
│   ├── web/          # Next.js frontend (port 3000)
│   ├── api/          # FastAPI middleware (port 8000)
│   └── nlp/          # NLP extraction pipeline (LangGraph agents) + Notion sync
├── packages/
│   └── shared/       # Shared TypeScript constants and types
├── infra/
│   ├── docker/       # Production Dockerfiles
│   ├── terraform/    # Azure IaC (7 modules)
│   └── k8s/          # Kustomize manifests (base + 3 overlays)
├── scripts/          # Schema init and seed scripts
└── .github/
    └── workflows/    # CI/CD pipelines
```

## Application Features

### Operational Layer (The Thread)

The Thread runs every Friday afternoon in a 2.5-hour block. The app manages the full lifecycle:

| Feature | Route | Description |
|---------|-------|-------------|
| Dashboard | `/` | Current cycle status, active session, quick actions |
| Schedule | `/schedule` | 12-week grid with lead/shadow assignments, create cycles |
| Session Workspace | `/sessions/{id}/workspace` | Week 1: Problem-Landscape Brief editor. Week 2: Position editor with lock workflow |
| Session Prep | `/sessions/{id}/prep` | Auto-generated prep brief, AI-powered thread prep, reading lists, workshop assignments |
| Evidence Vault | `/evidence-vault` | Filterable evidence entries by arc, proposition (P1/V1), and type |
| Live Fire | `/live-fire` | Track field usage of positions, submit entries, view metrics |
| Forge | `/forge` | Kanban board for the content pipeline (12 artefacts per cycle) |
| Fast Track | `/fast-track` | Onboarding digest of locked positions |

### Lock Workflow

Positions and Problem-Landscape Briefs follow a draft-to-locked lifecycle. Once locked, they can only be revised via Live Fire (field evidence of failure) or Flash (market disruption). Each revision creates a new version linked via `SUPERSEDES`.

### Thread Prep Generation

The prep page includes an AI-powered brief generator (`POST /scheduled-sessions/{id}/generate-prep`) backed by a LangGraph agent that:
1. Resolves arc structure data and determines week type
2. Pulls recent bookmarks and locked positions from Neo4j
3. Builds a context-rich prompt and maps bookmarks to PMF canvas anchors using Claude (via LangGraph StateGraph)
4. Produces a structured brief (sharpened questions, steelman, workshop criteria, reading assignments, flash checks)
5. Validates the output and persists the result to Neo4j

### Knowledge Graph

| Feature | Route | Description |
|---------|-------|-------------|
| Arc Explorer | `/arcs` | Force-directed graph of arcs with drill-down to bookmarks |
| Bridge Explorer | `/bridges` | Cross-arc connection visualisation |
| Objection Forge | `/objections` | CRUD for objection-response pairs |
| Topics | `/topics` | Topic explorer with co-occurrence |
| Sessions | `/sessions` | Session timeline with filters |
| Bookmarks | `/bookmarks` | All bookmarks grouped by theme |

## Prerequisites

- Node.js 20+ and pnpm 9+
- Python 3.10+
- Docker and Docker Compose
- (Optional) Terraform 1.5+, kubectl, KinD for cluster deployment
- (Optional) Azure CLI for cloud deployment

---

## Local Development (without Docker)

### 1. Environment

```bash
cp .env.example .env
# Edit .env with your Neo4j password, Notion keys, and Anthropic API key
```

### 2. Neo4j

Start a local Neo4j instance (Docker is easiest even when developing locally):

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/changeme \
  neo4j:5-community
```

Initialise the schema and seed data:

```bash
# Apply constraints and indexes (via the Neo4j container)
docker exec -i neo4j cypher-shell -u neo4j -p changeme < scripts/init-schema.cypher

# Seed with fixture data (6 arcs, propositions, sample bookmarks)
cd apps/api
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
python ../../scripts/seed.py
```

### 3. API

```bash
cd apps/api
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

API docs are at [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. Frontend

```bash
pnpm install
pnpm --filter web dev
```

Open [http://localhost:3000](http://localhost:3000).

### 5. NLP Pipeline (optional)

```bash
cd apps/nlp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Process a single session
python main.py --session-id <id>

# Process all unprocessed sessions
python main.py --batch
```

### 6. Notion Sync (optional)

Requires `NOTION_API_KEY`, `NOTION_BOOKMARKS_DB_ID`, and `NOTION_SESSIONS_DB_ID` in `.env`.

```bash
cd apps/nlp

# Sync all databases
python -m sync.runner --full

# Sync bookmarks only
python -m sync.runner --db bookmarks

# Dry run (fetch and transform, do not submit)
python -m sync.runner --dry-run
```

### Running Tests

```bash
# API (from apps/api with venv active)
pytest -v                           # All tests
pytest -v -m "not integration"      # Unit only
pytest -v -m integration            # Integration (requires Docker)

# Frontend (from repo root)
pnpm --filter web test              # Vitest
pnpm --filter web typecheck         # TypeScript

# NLP (from apps/nlp with venv active)
pytest -v
```

---

## Docker Compose

The simplest way to run the full stack. All three services plus Neo4j start together.

```bash
cp .env.example .env
# Edit .env as needed

docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | [http://localhost:3000](http://localhost:3000) |
| API | [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Neo4j Browser | [http://localhost:7474](http://localhost:7474) |

To seed the database after the stack is healthy:

```bash
# Apply constraints and indexes (pipe the file into cypher-shell inside the container)
docker compose exec -T neo4j cypher-shell -u neo4j -p changeme < scripts/init-schema.cypher

# Seed fixture data (run from the repo root with the API venv active)
cd apps/api && source .venv/bin/activate
python ../../scripts/seed.py
```

To stop:

```bash
docker compose down           # Stop and remove containers
docker compose down -v        # Also remove the Neo4j data volume
```

---

## Kubernetes via KinD

Run the full stack in a local Kubernetes cluster using [KinD](https://kind.sigs.k8s.io/).

### 1. Create a cluster

```bash
kind create cluster --name valliance-graph
```

### 2. Build and load images

```bash
# Build production images
docker build -t valliance-graph-web:latest -f infra/docker/web.Dockerfile apps/web
docker build -t valliance-graph-api:latest -f infra/docker/api.Dockerfile apps/api
docker build -t valliance-graph-nlp:latest -f infra/docker/nlp.Dockerfile apps/nlp

# Load into the KinD cluster
kind load docker-image valliance-graph-web:latest --name valliance-graph
kind load docker-image valliance-graph-api:latest --name valliance-graph
kind load docker-image valliance-graph-nlp:latest --name valliance-graph
```

### 3. Create secrets

```bash
kubectl create namespace valliance-graph

kubectl create secret generic valliance-graph-secrets \
  --namespace valliance-graph \
  --from-literal=neo4j-password=changeme \
  --from-literal=notion-api-key="${NOTION_API_KEY}" \
  --from-literal=anthropic-api-key="${ANTHROPIC_API_KEY}"
```

### 4. Apply the dev overlay

```bash
kubectl apply -k infra/k8s/overlays/dev
```

This creates in the `valliance-graph` namespace:

| Resource | Type | Notes |
|----------|------|-------|
| web | Deployment + Service + HPA | 1 replica, scales to 2 |
| api | Deployment + Service + HPA | 1 replica, scales to 3 |
| neo4j | StatefulSet + Service + PVC | 1 replica, 50Gi storage |
| nlp | CronJob | Hourly, 30 min deadline |
| ingress | Ingress | Routes `/` to web, `/api/` to api |

### 5. Access the services

With KinD, port-forward to access locally:

```bash
# Frontend
kubectl port-forward -n valliance-graph svc/web 3000:3000 &

# API
kubectl port-forward -n valliance-graph svc/api 8000:8000 &

# Neo4j Browser
kubectl port-forward -n valliance-graph svc/neo4j 7474:7474 7687:7687 &
```

### 6. Initialise the database

```bash
# Port-forward Neo4j bolt if not already done
kubectl port-forward -n valliance-graph svc/neo4j 7687:7687 &

# Apply schema (pipe into the Neo4j pod)
kubectl exec -n valliance-graph -i statefulset/neo4j -- cypher-shell -u neo4j -p changeme < scripts/init-schema.cypher

# Seed data
cd apps/api && source .venv/bin/activate
python ../../scripts/seed.py
```

### 7. Tear down

```bash
kind delete cluster --name valliance-graph
```

---

## Azure (AKS)

Production deployment to Azure Kubernetes Service using Terraform.

### 1. Bootstrap Terraform state

Run once per Azure subscription:

```bash
chmod +x infra/scripts/bootstrap-state.sh
./infra/scripts/bootstrap-state.sh
```

This creates:
- Resource group: `valliance-graph-tfstate`
- Storage account: `valliancegraphtfstate` (uksouth, LRS, TLS 1.2)
- Blob container: `tfstate`

### 2. Provision infrastructure

```bash
cd infra/terraform

# Initialise with the remote backend
terraform init

# Review the plan for the target environment
terraform plan -var-file=environments/dev.tfvars

# Apply (requires manual confirmation)
terraform apply -var-file=environments/dev.tfvars
```

Terraform provisions seven modules:

| Module | Resources |
|--------|-----------|
| networking | VNet, subnets (aks-nodes, aks-pods, services), NSG |
| aks | AKS cluster with system + user node pools, RBAC, managed identity |
| acr | Azure Container Registry (Standard for dev, Premium for prod) |
| keyvault | Azure Key Vault with soft delete, AKS identity access |
| storage | Blob storage for Terraform state |
| monitoring | Log Analytics workspace |
| dns | Azure DNS zone |

### 3. Configure kubectl

```bash
az aks get-credentials \
  --resource-group rg-valliance-graph-dev \
  --name aks-valliance-graph-dev
```

### 4. Push images to ACR

```bash
ACR_NAME=$(terraform output -raw acr_login_server)

az acr login --name "$ACR_NAME"

docker build -t "$ACR_NAME/valliance-graph-web:latest" -f infra/docker/web.Dockerfile apps/web
docker build -t "$ACR_NAME/valliance-graph-api:latest" -f infra/docker/api.Dockerfile apps/api
docker build -t "$ACR_NAME/valliance-graph-nlp:latest" -f infra/docker/nlp.Dockerfile apps/nlp

docker push "$ACR_NAME/valliance-graph-web:latest"
docker push "$ACR_NAME/valliance-graph-api:latest"
docker push "$ACR_NAME/valliance-graph-nlp:latest"
```

### 5. Create secrets in Key Vault

```bash
KV_NAME=$(terraform output -raw keyvault_name)

az keyvault secret set --vault-name "$KV_NAME" --name neo4j-password --value "<password>"
az keyvault secret set --vault-name "$KV_NAME" --name notion-api-key --value "<key>"
az keyvault secret set --vault-name "$KV_NAME" --name anthropic-api-key --value "<key>"
az keyvault secret set --vault-name "$KV_NAME" --name azure-ad-client-secret --value "<secret>"
```

### 6. Deploy to the cluster

```bash
chmod +x infra/scripts/deploy.sh

# Deploy to dev
./infra/scripts/deploy.sh dev

# Deploy to staging (after manual approval)
./infra/scripts/deploy.sh staging

# Deploy to prod
./infra/scripts/deploy.sh prod
```

The deploy script validates manifests with a dry-run, applies the kustomize overlay, and waits for rollout completion (300s timeout).

### Environment Sizing

| Property | Dev | Staging | Prod |
|----------|-----|---------|------|
| AKS system nodes | 1x Standard_D2s_v3 | 2x Standard_D2s_v3 | 2x Standard_D4s_v3 |
| AKS user nodes | 2x Standard_D2s_v3 | 3x Standard_D4s_v3 | 5x Standard_D4s_v3 |
| Neo4j storage | 50Gi | 100Gi | 200Gi |
| ACR SKU | Standard | Standard | Premium |
| Domain | dev.graph.valliance.dev | staging.graph.valliance.dev | graph.valliance.dev |

### 7. Tear down

```bash
cd infra/terraform
terraform destroy -var-file=environments/dev.tfvars
```

---

## CI/CD

GitHub Actions runs on push to `main` and on pull requests.

| Job | What it does |
|-----|-------------|
| Lint | ruff (Python), eslint (TypeScript) |
| Type check | mypy (Python), tsc (TypeScript) |
| Test | pytest (API, NLP), vitest (frontend) with coverage |
| Build | Docker images for web, api, nlp |
| Terraform | `terraform validate` and format check |

On merge to `main`, the deploy workflow builds images, pushes to ACR, and deploys through dev, staging, and prod with manual approval gates between each.

---

## API Overview

All endpoints are prefixed with `/api/v1/`. Full interactive docs at `/docs`.

### Operational Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /cycles | List all cycles |
| GET | /cycles/current | Current cycle with active session and days until next |
| POST | /cycles | Create a cycle (generates 12 scheduled sessions) |
| GET | /cycles/{id}/schedule | 12-week schedule with lead/shadow assignments |
| PUT | /cycles/{id}/schedule/{session_id} | Update lead/shadow assignment |
| GET | /scheduled-sessions/{id} | Session detail |
| POST | /briefs | Create a Problem-Landscape Brief (draft) |
| GET | /briefs/{id} | Brief with landscape grid |
| PUT | /briefs/{id} | Update brief (draft only) |
| POST | /briefs/{id}/lock | Lock a brief |
| POST | /positions | Create a position (draft) |
| PUT | /positions/{id} | Update position (draft/under_revision only) |
| POST | /positions/{id}/lock | Lock position (validates required fields) |
| POST | /positions/{id}/revise | Create new version of locked position |
| GET | /positions/{id}/versions | Version history |
| POST | /live-fire | Submit a Live Fire entry |
| GET | /live-fire | List entries with filters |
| GET | /live-fire/metrics | Per-position usage metrics |
| POST | /flashes | Submit a Flash |
| GET | /flashes | List flashes |
| GET | /flashes/pending | Pending flashes |
| PUT | /flashes/{id} | Update flash status |
| GET | /evidence-vault | Filtered evidence (arc, proposition, type) |
| POST | /forge | Create a Forge assignment |
| GET | /forge | List assignments |
| PUT | /forge/{id} | Update assignment (validated status transitions) |
| GET | /forge/tracker | Cycle artefact tracker |
| POST | /scheduled-sessions/{id}/generate-prep | Generate AI thread prep brief |
| POST | /scheduled-sessions/{id}/regenerate-prep | Regenerate thread prep brief |
| GET | /scheduled-sessions/{id}/thread-prep | Get persisted thread prep brief |
| GET | /scheduled-sessions/{id}/prep-brief | Auto-generated prep brief |
| POST | /scheduled-sessions/{id}/workshop-assignments | Assign workshop players |
| POST | /scheduled-sessions/{id}/reading-list | Assign reading |

### Knowledge Graph Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Liveness probe with Neo4j connectivity |
| GET | /arcs | List arcs with position counts |
| GET | /arcs/{name} | Arc detail with bookmarks |
| GET | /arcs/{name}/bookmarks | Paginated bookmarks for an arc |
| GET | /arcs/bridges | Cross-arc bridges |
| GET | /bookmarks | Paginated bookmarks (filter by topic, theme) |
| GET | /positions | List positions (filter by arc, status, proposition) |
| GET | /positions/{id} | Position detail with arguments and evidence |
| GET | /positions/{id}/arguments | Argument map |
| GET | /positions/{id}/evidence-trail | Evidence provenance chain |
| GET | /sessions | Session timeline (filter by arc, person, date range) |
| GET | /topics | Topics with bookmark counts |
| GET | /search?q=... | Cross-entity full-text search |
| GET | /bridges | Cross-arc bridge list |
| GET | /objections | Objection-response pairs |
| POST | /enrichment/arguments | Batch create arguments (NLP pipeline) |
| POST | /sync/bookmarks | Upsert bookmarks (Notion sync) |
| POST | /sync/sessions | Upsert sessions (Notion sync) |

Response envelope: `{"data": ..., "meta": {"count": N}}` for collections, `{"data": ...}` for singles.
Error envelope: `{"error": {"code": "NOT_FOUND", "message": "..."}}` with appropriate HTTP status.

---

## Licence

Proprietary. Valliance internal use only.
