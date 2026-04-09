terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

locals {
  common_tags = {
    project     = "valliance-graph"
    environment = var.environment
    managed_by  = "terraform"
  }
}

module "networking" {
  source = "./modules/networking"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  vnet_address_space  = var.vnet_address_space
  tags                = local.common_tags
}

module "acr" {
  source = "./modules/acr"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  acr_sku             = var.acr_sku
  tags                = local.common_tags
}

module "aks" {
  source = "./modules/aks"

  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  environment           = var.environment
  kubernetes_version    = var.kubernetes_version
  system_node_count     = var.system_node_count
  system_node_vm_size   = var.system_node_vm_size
  user_node_count       = var.user_node_count
  user_node_vm_size     = var.user_node_vm_size
  vnet_subnet_id        = module.networking.aks_nodes_subnet_id
  pod_subnet_id         = module.networking.aks_pods_subnet_id
  acr_id                = module.acr.acr_id
  log_analytics_id      = module.monitoring.log_analytics_workspace_id
  tags                  = local.common_tags
}

module "keyvault" {
  source = "./modules/keyvault"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  tenant_id           = data.azurerm_client_config.current.tenant_id
  aks_identity_id     = module.aks.kubelet_identity_object_id
  tags                = local.common_tags
}

module "storage" {
  source = "./modules/storage"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  tags                = local.common_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  tags                = local.common_tags
}

module "dns" {
  source = "./modules/dns"

  resource_group_name = azurerm_resource_group.main.name
  domain_name         = var.domain_name
  tags                = local.common_tags
}
