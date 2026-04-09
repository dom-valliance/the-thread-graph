output "acr_id" {
  description = "ID of the container registry"
  value       = azurerm_container_registry.main.id
}

output "login_server" {
  description = "Login server URL"
  value       = azurerm_container_registry.main.login_server
}

output "acr_name" {
  description = "Name of the container registry"
  value       = azurerm_container_registry.main.name
}
