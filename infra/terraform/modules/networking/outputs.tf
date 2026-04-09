output "vnet_id" {
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}

output "aks_nodes_subnet_id" {
  description = "ID of the AKS nodes subnet"
  value       = azurerm_subnet.aks_nodes.id
}

output "aks_pods_subnet_id" {
  description = "ID of the AKS pods subnet"
  value       = azurerm_subnet.aks_pods.id
}

output "services_subnet_id" {
  description = "ID of the services subnet"
  value       = azurerm_subnet.services.id
}
