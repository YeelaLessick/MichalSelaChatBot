module "resource_group" {
  source = "./resource_group"

  location            = var.location
  resource_group_name = var.resource_group_name
}

module "storage_account" {
  source = "./storage_account"

  storage_account_name     = "samichalselaprod01"
  location                = var.location
  resource_group_name     = module.resource_group.resource_group_name
  account_tier            = "Standard"
  account_replication_type = "LRS"
  account_kind            = "StorageV2"
  access_tier             = "Hot"

  depends_on = [module.resource_group]
}

module "azure_bot" {
  source = "./azure_bot"

  bot_name            = "michalSelaBot"
  location            = var.location
  resource_group_name = module.resource_group.resource_group_name
  sku                 = "F0"

  depends_on = [module.resource_group]
}

module "app_service" {
  source = "./app_service"

  resource_group_name   = module.resource_group.resource_group_name
  location             = var.location
  app_service_plan_name = "michalsela-asp"
  app_service_name     = "michalsela-webapp"
  sku_name             = "B1"

  # Bot Framework integration
  microsoft_app_id       = module.azure_bot.app_id
  microsoft_app_tenant_id = module.azure_bot.tenant_id

  # App configuration
  linux_fx_version    = "PYTHON|3.12"
  always_on          = false
  scm_type           = "GitHubAction"

  # Optional: Configure source control
  repo_url    = "https://github.com/YeelaLessick/MichalSelaChatBot"
  repo_branch = "main"

  # Additional app settings including bot credentials
  additional_app_settings = {
    ENVIRONMENT = "production"
    MicrosoftAppPassword = module.azure_bot.app_secret
  }

  depends_on = [module.resource_group, module.azure_bot]
}
