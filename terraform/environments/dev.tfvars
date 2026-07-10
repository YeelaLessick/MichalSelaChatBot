# Development Environment Configuration
location            = "westeurope"
resource_group_name = "michalselabot-dev-rg"
subscription_id     = "acd75acf-314c-435d-b215-b212f1586640"
environment         = "dev"

# Storage Account
storage_account_name = "samichalseladev01"

# Azure Bot
bot_name = "michalSelaBot-dev"
bot_sku  = "F0"
bot_messaging_endpoint = "https://michalsela-webapp-dev.azurewebsites.net/api/messages"

# App Service
app_service_plan_name = "michalsela-asp-dev"
app_service_name      = "michalsela-webapp-dev"
sku_name              = "B1"  # Basic tier for development (F1 has capacity issues)

# Repository Configuration
repo_url    = "https://github.com/YeelaLessick/MichalSelaChatBot"
repo_branch = "develop"  # Use develop branch for dev environment

# Azure OpenAI
openai_account_name     = "michalsela-openai-dev"
openai_deployment_name  = "gpt-4.1"

# PostgreSQL Flexible Server (~$13/mo on B_Standard_B1ms)
postgres_server_name   = "michalsela-pg-dev"
postgres_location      = "westeurope"
postgres_database_name = "chatbot"
postgres_sku_name      = "B_Standard_B1ms"
postgres_storage_mb    = 32768
# Optional: set to your Entra user object ID for psql access
# postgres_entra_admin_object_id      = "00000000-0000-0000-0000-000000000000"
# postgres_entra_admin_principal_name = "you@example.com"
postgres_firewall_rules = {}

# Communication Service
communication_service_name = "michalsela-communication-dev"
communication_data_location = "Europe"

# Virtual Network
vnet_name                   = "vnet-michalsela-dev"
vnet_address_space         = ["10.1.0.0/16"]
subnet_name                = "default"
subnet_address_prefixes    = ["10.1.0.0/24"]
subnet_service_endpoints   = ["Microsoft.Storage", "Microsoft.CognitiveServices"]

# Managed Identities
app_service_identity_name  = "michalsela-webapp-dev"
bot_identity_name         = "michalSelaBot-dev"
openai_identity_name      = "michalsela-openai-dev"

# Weekly summary email settings
weekly_summary_enabled      = true
weekly_summary_recipient    = "michalsela@info.com"
weekly_summary_timezone     = "Asia/Jerusalem"
weekly_summary_send_hour    = 9

# SMTP settings (uncomment and set real values to enable email delivery)
# smtp_server   = "smtp.example.com"
# smtp_port     = 587
# smtp_username = "mailer@example.com"
# smtp_password = "<set-via-secure-secret>"
# smtp_from     = "mailer@example.com"

# Tags
tags = {
  Environment = "dev"
  Project     = "MichalSelaBot"
  Owner       = "YeelaLessick"
}
