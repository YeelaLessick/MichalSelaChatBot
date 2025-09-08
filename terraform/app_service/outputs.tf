output "app_service_id" {
  description = "The ID of the App Service"
  value       = azurerm_linux_web_app.main.id
}

output "app_service_name" {
  description = "The name of the App Service"
  value       = azurerm_linux_web_app.main.name
}

output "app_service_default_hostname" {
  description = "The default hostname of the App Service"
  value       = azurerm_linux_web_app.main.default_hostname
}

output "app_service_outbound_ip_addresses" {
  description = "The outbound IP addresses of the App Service"
  value       = azurerm_linux_web_app.main.outbound_ip_addresses
}

output "app_service_possible_outbound_ip_addresses" {
  description = "The possible outbound IP addresses of the App Service"
  value       = azurerm_linux_web_app.main.possible_outbound_ip_addresses
}

output "app_service_plan_id" {
  description = "The ID of the App Service Plan"
  value       = azurerm_service_plan.main.id
}

output "app_service_plan_name" {
  description = "The name of the App Service Plan"
  value       = azurerm_service_plan.main.name
}

output "app_service_identity_principal_id" {
  description = "The Principal ID of the App Service's managed identity"
  value       = length(azurerm_linux_web_app.main.identity) > 0 ? azurerm_linux_web_app.main.identity[0].principal_id : null
}

output "app_service_identity_tenant_id" {
  description = "The Tenant ID of the App Service's managed identity"
  value       = length(azurerm_linux_web_app.main.identity) > 0 ? azurerm_linux_web_app.main.identity[0].tenant_id : null
}

output "app_service_site_credential" {
  description = "The site credentials for the App Service"
  value       = azurerm_linux_web_app.main.site_credential
  sensitive   = true
}
