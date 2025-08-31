output "app_id" {
  description = "Application (client) ID of the managed identity"
  value       = var.managed_identity_client_id
}

output "tenant_id" {
  description = "The Tenant ID of the bot's managed identity"
  value       = data.azuread_client_config.current.tenant_id
}

output "bot_service_id" {
  description = "The ID of the Azure Bot Service"
  value       = azurerm_bot_service_azure_bot.michalselabot.id
}
