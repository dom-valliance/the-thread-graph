# Module: Infrastructure

Azure target architecture with Terraform IaC, Docker containerisation, and Kubernetes (AKS) orchestration.

---

## Technology

- Azure (primary cloud)
- Terraform 1.7+ (infrastructure as code)
- Docker (containerisation)
- Azure Kubernetes Service (AKS) for orchestration
- Azure Container Registry (ACR) for image storage
- Azure Blob Storage for Terraform state
- Azure Key Vault for secrets
- Azure AD for authentication
- GitHub Actions for CI/CD

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│  Azure Resource Group: rg-valliance-graph-{env}      │
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │    AKS       │  │   ACR        │  │  Key Vault  │ │
│  │  Cluster     │  │  Images      │  │  Secrets    │ │
│  │             │  │              │  │             │ │
│  │  ┌────────┐ │  └──────────────┘  └─────────────┘ │
│  │  │ web    │ │                                     │
│  │  │ (Next) │ │  ┌──────────────┐  ┌─────────────┐ │
│  │  ├────────┤ │  │  Blob Store  │  │   Azure AD  │ │
│  │  │ api    │ │  │  TF State    │  │   Auth      │ │
│  │  │ (Fast) │ │  └──────────────┘  └─────────────┘ │
│  │  ├────────┤ │                                     │
│  │  │ neo4j  │ │  ┌──────────────┐                  │
│  │  │        │ │  │  Log         │                  │
│  │  ├────────┤ │  │  Analytics   │                  │
│  │  │ nlp    │ │  │  Workspace   │                  │
│  │  │ (cron) │ │  └──────────────┘                  │
│  │  └────────┘ │                                     │
│  └─────────────┘                                     │
└──────────────────────────────────────────────────────┘
```

## Directory Structure

```
infra/
├── terraform/
│   ├── main.tf                 # Root module, provider config
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   ├── backend.tf              # Azure Blob Storage state backend
│   ├── modules/
│   │   ├── aks/                # AKS cluster module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── acr/                # Container registry module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── keyvault/           # Key Vault module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── storage/            # Blob storage for TF state
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── networking/         # VNet, subnets, NSGs
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── monitoring/         # Log Analytics, alerts
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── dns/                # Azure DNS for custom domain
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   └── environments/
│       ├── dev.tfvars
│       ├── staging.tfvars
│       └── prod.tfvars
├── docker/
│   ├── web.Dockerfile          # Next.js multi-stage build
│   ├── api.Dockerfile          # FastAPI multi-stage build
│   ├── nlp.Dockerfile          # NLP pipeline image
│   └── neo4j.Dockerfile        # Neo4j with APOC plugin (dev only; prod uses Helm chart)
├── k8s/
│   ├── base/                   # Base manifests (kustomize)
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── web/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── hpa.yaml
│   │   ├── api/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── hpa.yaml
│   │   ├── neo4j/
│   │   │   ├── statefulset.yaml
│   │   │   ├── service.yaml
│   │   │   └── pvc.yaml
│   │   ├── nlp/
│   │   │   └── cronjob.yaml
│   │   ├── ingress.yaml
│   │   └── secrets.yaml        # ExternalSecret referencing Key Vault
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml
│       │   └── patches/
│       ├── staging/
│       │   ├── kustomization.yaml
│       │   └── patches/
│       └── prod/
│           ├── kustomization.yaml
│           └── patches/
└── scripts/
    ├── bootstrap-state.sh      # One-time TF state backend setup
    └── deploy.sh               # CI deployment helper
```

## Terraform Modules

### AKS Cluster

- Kubernetes version: 1.29+
- System node pool: 2 nodes, Standard_D2s_v3
- User node pool: 2-5 nodes (autoscaler), Standard_D4s_v3
- Azure CNI networking
- RBAC enabled, Azure AD integration
- OMS agent for monitoring

### ACR

- SKU: Standard (dev/staging), Premium (prod for geo-replication)
- Admin user disabled; AKS authenticates via managed identity
- Image retention policy: keep last 10 tags per repository

### Key Vault

- Stores: Neo4j password, Notion API key, Anthropic API key, Azure AD client secret
- Access policy: AKS managed identity has get/list on secrets
- Soft delete enabled, purge protection on prod

### Networking

- VNet with three subnets: AKS nodes, AKS pods, services
- NSG rules: restrict Neo4j bolt port to AKS pod subnet only
- No public IP on Neo4j

## Docker Images

### web.Dockerfile (Next.js)

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

### api.Dockerfile (FastAPI)

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv && uv pip install --system -e "."

# Stage 2: Production
FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Kubernetes Resources

### Web Deployment

- Replicas: 2 (dev), 3 (prod)
- HPA: scale on CPU 70%, min 2, max 6
- Liveness: HTTP GET /
- Readiness: HTTP GET /
- Resource limits: 512Mi memory, 500m CPU

### API Deployment

- Replicas: 2 (dev), 3 (prod)
- HPA: scale on CPU 70%, min 2, max 8
- Liveness: HTTP GET /api/v1/health
- Readiness: HTTP GET /api/v1/health
- Resource limits: 1Gi memory, 1000m CPU

### Neo4j StatefulSet

- Replicas: 1 (single instance; clustering in Phase 5 if needed)
- Persistent volume: 50Gi (dev), 200Gi (prod), Azure Managed Disk
- Liveness: TCP check on bolt port 7687
- Resource limits: 4Gi memory, 2000m CPU
- No HPA; vertical scaling only

### NLP CronJob

- Schedule: `0 * * * *` (hourly, checks for new sessions)
- Restart policy: OnFailure
- Active deadline: 1800 seconds (30 minutes max)
- Resource limits: 2Gi memory, 1000m CPU

### Ingress

- NGINX Ingress Controller
- TLS via cert-manager + Let's Encrypt
- Routes: `/` to web service, `/api/` to api service
- Rate limiting on API endpoints

## CI/CD Pipeline (GitHub Actions)

```
on push to feature branch:
  → lint (frontend + API)
  → type check (frontend + API)
  → unit tests (frontend + API + NLP)
  → build Docker images
  → scan images for CVEs (trivy)
  → terraform validate
  → terraform plan (output as PR comment)

on merge to main:
  → all of the above
  → push images to ACR
  → deploy to dev (kubectl apply)
  → integration tests against dev
  → manual approval gate
  → deploy to staging
  → smoke tests
  → manual approval gate
  → deploy to prod
```

## Environments

| Property | Dev | Staging | Prod |
|----------|-----|---------|------|
| AKS nodes | 2 | 3 | 5 |
| Neo4j storage | 50Gi | 100Gi | 200Gi |
| API replicas | 2 | 2 | 3 |
| Web replicas | 1 | 2 | 3 |
| Domain | dev.graph.valliance.ai | staging.graph.valliance.ai | graph.valliance.ai |
| TLS | Let's Encrypt staging | Let's Encrypt staging | Let's Encrypt prod |

## Local Development

```bash
# Start all services locally
docker compose up

# Services:
#   web:   http://localhost:3000
#   api:   http://localhost:8000
#   neo4j: bolt://localhost:7687, http://localhost:7474 (browser)

# Terraform
cd infra/terraform
terraform init -backend-config=environments/dev.tfvars
terraform plan -var-file=environments/dev.tfvars
# terraform apply requires manual approval (denied in settings.json)
```

## Security

- No secrets in code, Docker images, or Terraform state outputs.
- All secrets in Azure Key Vault, injected into pods via ExternalSecrets Operator.
- Neo4j bolt port not exposed outside the cluster.
- Azure AD JWT validation on every API request.
- Docker images scanned with Trivy in CI; builds fail on critical/high CVEs.
- Terraform state encrypted at rest in Azure Blob Storage.
