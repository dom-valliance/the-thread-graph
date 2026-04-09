#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="valliance-graph-tfstate"
STORAGE_ACCOUNT="valliancegraphtfstate"
CONTAINER_NAME="tfstate"
LOCATION="uksouth"

echo "Creating resource group: ${RESOURCE_GROUP}"
az group create \
  --name "${RESOURCE_GROUP}" \
  --location "${LOCATION}"

echo "Creating storage account: ${STORAGE_ACCOUNT}"
az storage account create \
  --name "${STORAGE_ACCOUNT}" \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${LOCATION}" \
  --sku Standard_LRS \
  --encryption-services blob \
  --min-tls-version TLS1_2

echo "Creating blob container: ${CONTAINER_NAME}"
az storage container create \
  --name "${CONTAINER_NAME}" \
  --account-name "${STORAGE_ACCOUNT}"

echo "Enabling versioning on storage account"
az storage account blob-service-properties update \
  --account-name "${STORAGE_ACCOUNT}" \
  --resource-group "${RESOURCE_GROUP}" \
  --enable-versioning true

echo "Terraform state backend bootstrapped successfully."
echo "Resource group: ${RESOURCE_GROUP}"
echo "Storage account: ${STORAGE_ACCOUNT}"
echo "Container: ${CONTAINER_NAME}"
