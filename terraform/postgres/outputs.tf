output "server_id" {
  description = "Resource ID of the PostgreSQL Flexible Server"
  value       = azurerm_postgresql_flexible_server.main.id
}

output "server_name" {
  description = "Server name"
  value       = azurerm_postgresql_flexible_server.main.name
}

output "fqdn" {
  description = "Fully qualified domain name (use as host)"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "database_name" {
  description = "Name of the chatbot database"
  value       = azurerm_postgresql_flexible_server_database.main.name
}

# Convenience: full host:port pair, suitable for env vars
output "host_port" {
  description = "host:port string"
  value       = "${azurerm_postgresql_flexible_server.main.fqdn}:5432"
}
