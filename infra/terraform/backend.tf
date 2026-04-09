terraform {
  backend "azurerm" {
    resource_group_name  = "valliance-graph-tfstate"
    storage_account_name = "valliancegraphtfstate"
    container_name       = "tfstate"
    key                  = "valliance-graph.tfstate"
  }
}
