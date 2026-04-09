output "dns_zone_id" {
  description = "ID of the DNS zone"
  value       = azurerm_dns_zone.main.id
}

output "name_servers" {
  description = "Name servers for the DNS zone"
  value       = azurerm_dns_zone.main.name_servers
}
