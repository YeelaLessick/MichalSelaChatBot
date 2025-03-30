output "private_dns_zone_id" {
  description = "The ID of the private DNS zone"
  value       = azurerm_private_dns_zone.main.id
}

output "private_dns_zone_name" {
  description = "The name of the private DNS zone"
  value       = azurerm_private_dns_zone.main.name
}

output "vnet_link_id" {
  description = "The ID of the virtual network link to the DNS zone"
  value       = azurerm_private_dns_zone_virtual_network_link.main.id
}

output "vnet_link_name" {
  description = "The name of the virtual network link to the DNS zone"
  value       = azurerm_private_dns_zone_virtual_network_link.main.name
}
