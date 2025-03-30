resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku_name            = "B1" 
  os_type             = "Linux"
}

resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = "1"
    MicrosoftAppId                 = var.microsoft_app_id
    MicrosoftAppTenantId           = var.microsoft_app_tenant_id
    MicrosoftAppType               = "ManagedIdentity"
  }

  https_only = true

  site_config {
    always_on                 = false
    ftps_state                = "FtpsOnly"
    http2_enabled             = false
    remote_debugging_enabled  = false
    vnet_route_all_enabled    = true
    websockets_enabled        = false
  }

  logs {
    application_logs {
      file_system_level = "Off"
    }

    http_logs {
      file_system {
        retention_in_days = 0
        retention_in_mb   = 35
      }
    }
  }

  identity {
    type = "SystemAssigned" # Enables system-assigned managed identity
  }
}

# Configure Source Control
resource "null_resource" "configure_source_control" {
  provisioner "local-exec" {
    command = <<EOT
az webapp deployment source config \
  --name ${azurerm_linux_web_app.main.name} \
  --resource-group ${azurerm_resource_group.main.name} \
  --repo-url ${var.repo_url} \
  --branch ${var.repo_branch} \
  --manual-integration false
EOT
  }
}
