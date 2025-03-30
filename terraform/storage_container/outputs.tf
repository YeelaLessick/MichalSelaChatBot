output "storage_container_id" {
  description = "The ID of the storage container"
  value       = azurerm_storage_container.main.id
}

output "storage_container_name" {
  description = "The name of the storage container"
  value       = azurerm_storage_container.main.name
}
