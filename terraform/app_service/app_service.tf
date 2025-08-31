# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = var.sku_name
  os_type             = "Linux"
}

# Linux Web App
resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.main.id

  # App Settings
  app_settings = merge(
    {
      SCM_DO_BUILD_DURING_DEPLOYMENT = "1"
    },
    var.microsoft_app_id != null ? {
      MicrosoftAppId       = var.microsoft_app_id
      MicrosoftAppTenantId = var.microsoft_app_tenant_id
      MicrosoftAppType     = "ManagedIdentity"
    } : {},
    var.azure_openai_api_key != null ? {
      AZURE_OPENAI_API_KEY     = var.azure_openai_api_key
      AZURE_OPENAI_ENDPOINT    = var.azure_openai_endpoint
      AZURE_OPENAI_API_VERSION = var.azure_openai_api_version
      DEPLOYMENT_NAME          = var.azure_openai_deployment_name
    } : {},
    var.additional_app_settings
  )

  # Security and networking settings
  https_only                      = true
  client_affinity_enabled         = false
  client_certificate_enabled      = false
  client_certificate_mode         = "Required"
  public_network_access_enabled   = var.public_network_access_enabled
  virtual_network_subnet_id       = var.virtual_network_subnet_id

  site_config {
    always_on                     = var.always_on
    ftps_state                    = "FtpsOnly"
    http2_enabled                 = false
    minimum_tls_version           = "1.2"
    remote_debugging_enabled      = false
    scm_minimum_tls_version       = "1.2"
    use_32_bit_worker             = true
    vnet_route_all_enabled        = var.vnet_route_all_enabled
    websockets_enabled            = false

    application_stack {
      python_version = "3.12"
    }

    # Default documents
    default_documents = [
      "Default.htm",
      "Default.html",
      "Default.asp",
      "index.htm",
      "index.html",
      "iisstart.htm",
      "default.aspx",
      "index.php",
      "hostingstart.html"
    ]

    # IP Security Restrictions - Allow all by default
    ip_restriction {
      ip_address = "0.0.0.0/0"
      action     = "Allow"
      priority   = 2147483647
      name       = "Allow all"
    }

    # SCM IP Security Restrictions - Allow all by default
    scm_ip_restriction {
      ip_address = "0.0.0.0/0"
      action     = "Allow"
      priority   = 2147483647
      name       = "Allow all"
    }
  }

  # Logging configuration
  logs {
    application_logs {
      file_system_level = "Off"
    }

    http_logs {
      file_system {
        retention_in_days = 0
        retention_in_mb   = var.http_logs_retention_mb
      }
    }
  }

  # Managed Identity
  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      app_settings["WEBSITE_RUN_FROM_PACKAGE"],
    ]
  }
}

# Note: Basic publishing credentials policies are not supported in this provider version
# These would need to be configured manually or via Azure CLI

# Note: Source control configuration can be set up manually in Azure Portal
# or via Azure CLI outside of Terraform due to CLI command compatibility issues
# 
# To configure manually:
# 1. Go to Azure Portal > App Service > Deployment Center
# 2. Choose GitHub as source
# 3. Configure repository: https://github.com/YeelaLessick/MichalSelaChatBot
# 4. Set branch to: main
