resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-valliance-graph-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  dns_prefix          = "valliance-graph-${var.environment}"
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "system"
    node_count          = var.system_node_count
    vm_size             = var.system_node_vm_size
    vnet_subnet_id      = var.vnet_subnet_id
    pod_subnet_id       = var.pod_subnet_id
    os_disk_size_gb     = 50
    max_pods            = 50
    enable_auto_scaling = false

    node_labels = {
      "nodepool" = "system"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
    load_balancer_sku = "standard"
  }

  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
  }

  oms_agent {
    log_analytics_workspace_id = var.log_analytics_id
  }

  tags = var.tags
}

resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "user"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.user_node_vm_size
  node_count            = var.user_node_count
  vnet_subnet_id        = var.vnet_subnet_id
  pod_subnet_id         = var.pod_subnet_id
  os_disk_size_gb       = 50
  max_pods              = 50
  enable_auto_scaling   = false

  node_labels = {
    "nodepool" = "user"
  }

  tags = var.tags
}

resource "azurerm_role_assignment" "acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = var.acr_id
  skip_service_principal_aad_check = true
}
