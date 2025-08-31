output "communication_service_id" {
  description = "The ID of the Communication Service"
  value       = azurerm_communication_service.main.id
}

output "communication_service_primary_connection_string" {
  description = "The primary connection string of the Communication Service"
  value       = azurerm_communication_service.main.primary_connection_string
  sensitive   = true
}

output "communication_service_primary_key" {
  description = "The primary key of the Communication Service"
  value       = azurerm_communication_service.main.primary_key
  sensitive   = true
}
