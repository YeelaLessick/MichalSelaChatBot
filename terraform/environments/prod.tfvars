# Production Environment Configuration
location            = "westeurope"
resource_group_name = "michalselabot-prod-rg"
subscription_id     = "acd75acf-314c-435d-b215-b212f1586640"
environment         = "prod"

# Storage Account
storage_account_name = "samichalselaprod01"

# Azure Bot
bot_name = "michalSelaBot"
bot_sku  = "F0"
bot_messaging_endpoint = "https://michalsela-app.azurewebsites.net/api/messages"

# App Service
app_service_plan_name = "michalsela-asp-prod"
app_service_name      = "michalsela-app"
sku_name              = "B1"

# Repository Configuration
repo_url    = "https://github.com/YeelaLessick/MichalSelaChatBot"
repo_branch = "main"

# Azure OpenAI
openai_account_name     = "michalsela-openai"
openai_deployment_name  = "gpt-4.1"

# Cosmos DB
cosmosdb_name           = "michalsela-cosmos"
cosmosdb_enable_free_tier = true
cosmosdb_ip_range_filter = ""

# Communication Service
communication_service_name = "michalsela-communication"
communication_data_location = "Europe"

# Virtual Network
vnet_name                   = "vnet-michalsela"
vnet_address_space         = ["10.0.0.0/16"]
subnet_name                = "default"
subnet_address_prefixes    = ["10.0.0.0/24"]
subnet_service_endpoints   = ["Microsoft.Storage", "Microsoft.CognitiveServices"]

# Managed Identities
app_service_identity_name  = "michalsela-webapp"
bot_identity_name         = "michalSelaBot"
openai_identity_name      = "michalsela-openai"

# Tags
tags = {
  Environment = "prod"
  Project     = "MichalSelaBot"
  Owner       = "YeelaLessick"
}
