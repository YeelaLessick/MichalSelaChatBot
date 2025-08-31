output "identity_id" {
  description = "The ID of the managed identity"
  value       = azurerm_user_assigned_identity.identity.id
}

output "identity_principal_id" {
  description = "The principal ID of the managed identity"
  value       = azurerm_user_assigned_identity.identity.principal_id
}

output "identity_client_id" {
  description = "The client ID of the managed identity"
  value       = azurerm_user_assigned_identity.identity.client_id
}

output "identity_name" {
  description = "The name of the managed identity"
  value       = azurerm_user_assigned_identity.identity.name
}
