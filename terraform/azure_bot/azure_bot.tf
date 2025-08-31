# Get tenant information
data "azuread_client_config" "current" {}

# Azure Bot Service with Managed Identity
resource "azurerm_bot_service_azure_bot" "michalselabot" {
  name                = var.bot_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku

  microsoft_app_id        = var.managed_identity_client_id
  microsoft_app_tenant_id = data.azuread_client_config.current.tenant_id
  microsoft_app_type      = "UserAssignedMSI"
  microsoft_app_msi_id    = var.managed_identity_id
  endpoint                = var.messaging_endpoint
  
  tags = {
    environment = "dev"
  }
}
