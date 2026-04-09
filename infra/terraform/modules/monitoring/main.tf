resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-valliance-graph-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = var.tags
}

resource "azurerm_log_analytics_solution" "containers" {
  solution_name         = "ContainerInsights"
  workspace_resource_id = azurerm_log_analytics_workspace.main.id
  workspace_name        = azurerm_log_analytics_workspace.main.name
  location              = var.location
  resource_group_name   = var.resource_group_name

  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/ContainerInsights"
  }
}
