# Main Infrastructure Configuration
# Use with environment-specific .tfvars files

module "resource_group" {
  source = "./resource_group"

  location            = var.location
  resource_group_name = var.resource_group_name
}

# module "storage_account" {
#   source = "./storage_account"

#   storage_account_name     = var.storage_account_name
#   location                = var.location
#   resource_group_name     = module.resource_group.resource_group_name
#   account_tier            = "Standard"
#   account_replication_type = "LRS"
#   account_kind            = "StorageV2"
#   access_tier             = "Hot"

#   depends_on = [module.resource_group]
# }

module "azure_bot" {
  source = "./azure_bot"

  bot_name                   = var.bot_name
  location                   = var.location
  resource_group_name        = module.resource_group.resource_group_name
  sku                        = var.bot_sku
  messaging_endpoint         = var.bot_messaging_endpoint
  managed_identity_client_id = module.managed_identity_bot.identity_client_id
  managed_identity_id        = module.managed_identity_bot.identity_id

  depends_on = [module.resource_group, module.managed_identity_bot]
}

module "app_service" {
  source = "./app_service"

  resource_group_name   = module.resource_group.resource_group_name
  location             = var.location
  app_service_plan_name = var.app_service_plan_name
  app_service_name     = var.app_service_name
  sku_name             = var.sku_name

  # Bot Framework integration - using User-Assigned Managed Identity
  microsoft_app_id       = module.azure_bot.app_id
  microsoft_app_tenant_id = module.azure_bot.tenant_id
  managed_identity_id    = module.managed_identity_bot.identity_id

  # Azure OpenAI integration
  azure_openai_api_key        = module.azure_openai.openai_api_key
  azure_openai_endpoint       = module.azure_openai.openai_endpoint
  azure_openai_api_version    = var.azure_openai_api_version
  azure_openai_deployment_name = module.azure_openai.gpt4_deployment_name

  # Networking configuration
  virtual_network_subnet_id = module.virtual_network.subnet_id

  # App configuration
  linux_fx_version    = "PYTHON|3.12"
  always_on          = var.sku_name != "F1" ? true : false  # Always on not available for F1
  scm_type           = "GitHubAction"

  # Source control configuration
  repo_url    = var.repo_url
  repo_branch = var.repo_branch

  # Additional app settings
  additional_app_settings = {
    ENVIRONMENT = var.environment
  }

  depends_on = [module.resource_group, module.azure_bot, module.azure_openai, module.virtual_network, module.managed_identity_bot]
}

module "azure_openai" {
  source = "./azure_openai"

  openai_account_name = var.openai_account_name
  deployment_name     = var.openai_deployment_name
  location           = "eastus" 
  resource_group_name = module.resource_group.resource_group_name

  depends_on = [module.resource_group]
}

module "cosmosdb" {
  source = "./cosmosdb"

  cosmosdb_name       = var.cosmosdb_name
  location           = "israelcentral"
  resource_group_name = module.resource_group.resource_group_name
  enable_free_tier   = var.cosmosdb_enable_free_tier
  ip_range_filter    = var.cosmosdb_ip_range_filter
  tags               = var.tags

  depends_on = [module.resource_group]
}

module "communication_service" {
  source = "./communication_service"

  communication_service_name = var.communication_service_name
  resource_group_name       = module.resource_group.resource_group_name
  data_location            = var.communication_data_location
  tags                     = var.tags

  depends_on = [module.resource_group]
}

module "virtual_network" {
  source = "./virtual_network"

  vnet_name                   = var.vnet_name
  location                   = var.location
  resource_group_name        = module.resource_group.resource_group_name
  address_space              = var.vnet_address_space
  subnet_name                = var.subnet_name
  subnet_address_prefixes    = var.subnet_address_prefixes
  service_endpoints          = var.subnet_service_endpoints
  tags                       = var.tags

  depends_on = [module.resource_group]
}

module "managed_identity_app_service" {
  source = "./managed_identity"

  identity_name       = var.app_service_identity_name
  location           = var.location
  resource_group_name = module.resource_group.resource_group_name
  tags               = var.tags

  depends_on = [module.resource_group]
}

module "managed_identity_bot" {
  source = "./managed_identity"

  identity_name       = var.bot_identity_name
  location           = var.location
  resource_group_name = module.resource_group.resource_group_name
  tags               = var.tags

  depends_on = [module.resource_group]
}

module "managed_identity_openai" {
  source = "./managed_identity"

  identity_name       = var.openai_identity_name
  location           = var.location
  resource_group_name = module.resource_group.resource_group_name
  tags               = var.tags

  depends_on = [module.resource_group]
}
