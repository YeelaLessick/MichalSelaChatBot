# Get tenant information
data "azuread_client_config" "current" {}

# Azure Active Directory Application
resource "azuread_application" "bot_app" {
  display_name     = var.bot_name
  sign_in_audience = "AzureADandPersonalMicrosoftAccount" # For multi-tenant
  
  api {
    requested_access_token_version = 2
  }
}

# AAD Service Principal for the Application
resource "azuread_service_principal" "bot_sp" {
  client_id = azuread_application.bot_app.client_id
}

# AAD Application Password (Client Secret)
resource "azuread_application_password" "bot_password" {
  application_id = azuread_application.bot_app.object_id
  end_date       = "2099-12-31T23:59:59Z"
}

# Generate a secure password for the AAD App
resource "random_password" "bot_password" {
  length  = 32
  special = true
}

# Azure Bot Service
resource "azurerm_bot_channels_registration" "michalselabot" {
  name                = var.bot_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku

  microsoft_app_id = azuread_application.bot_app.client_id
}
