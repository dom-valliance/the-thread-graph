#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-}"

if [[ -z "${ENVIRONMENT}" ]]; then
  echo "Usage: $0 <environment>"
  echo "  environment: dev, staging, or prod"
  exit 1
fi

if [[ ! "${ENVIRONMENT}" =~ ^(dev|staging|prod)$ ]]; then
  echo "Invalid environment: ${ENVIRONMENT}. Must be one of: dev, staging, prod."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERLAY_DIR="${SCRIPT_DIR}/../k8s/overlays/${ENVIRONMENT}"

if [[ ! -d "${OVERLAY_DIR}" ]]; then
  echo "Overlay directory not found: ${OVERLAY_DIR}"
  exit 1
fi

echo "Deploying to ${ENVIRONMENT}..."

echo "Validating manifests with dry-run..."
kubectl apply -k "${OVERLAY_DIR}" --dry-run=client

echo "Applying manifests..."
kubectl apply -k "${OVERLAY_DIR}"

echo "Waiting for web deployment rollout..."
kubectl rollout status deployment/web -n valliance-graph --timeout=300s

echo "Waiting for api deployment rollout..."
kubectl rollout status deployment/api -n valliance-graph --timeout=300s

echo "Deployment to ${ENVIRONMENT} complete."
