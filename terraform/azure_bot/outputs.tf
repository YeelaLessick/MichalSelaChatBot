output "app_id" {
  description = "Application (client) ID of the AAD app"
  value       = azuread_application.bot_app.client_id
}

output "tenant_id" {
  description = "The Tenant ID of the bot's AAD App"
  value       = data.azuread_client_config.current.tenant_id
}

output "app_secret" {
  description = "Client secret for the AAD app"
  value       = azuread_application_password.bot_password.value
}

output "bot_service_id" {
  description = "The ID of the Azure Bot Service"
  value       = azurerm_bot_channels_registration.michalselabot.id
}
