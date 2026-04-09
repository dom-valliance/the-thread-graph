output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.cluster_name
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = module.aks.cluster_fqdn
}

output "acr_login_server" {
  description = "Login server URL for the container registry"
  value       = module.acr.login_server
}

output "keyvault_uri" {
  description = "URI of the Key Vault"
  value       = module.keyvault.vault_uri
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "dns_name_servers" {
  description = "Name servers for the DNS zone"
  value       = module.dns.name_servers
}
