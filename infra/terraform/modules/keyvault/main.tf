resource "azurerm_key_vault" "main" {
  name                       = "kv-valliance-${var.environment}"
  resource_group_name        = var.resource_group_name
  location                   = var.location
  tenant_id                  = var.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 30
  purge_protection_enabled   = true

  access_policy {
    tenant_id = var.tenant_id
    object_id = var.aks_identity_id

    secret_permissions = [
      "Get",
      "List",
    ]
  }

  tags = var.tags
}
