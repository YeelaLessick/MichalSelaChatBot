variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
  default     = "westeurope"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the storage account"
  type        = string
}

variable "bot_name" {
  description = "Name of the Azure Bot"
  type        = string
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
}

variable "app_service_name" {
  description = "Name of the App Service"
  type        = string
}

variable "sku_name" {
  description = "SKU for the App Service Plan"
  type        = string
  default     = "B1"
}

variable "bot_sku" {
  description = "SKU for the Azure Bot"
  type        = string
  default     = "F0"
}

variable "bot_messaging_endpoint" {
  description = "The messaging endpoint for the bot"
  type        = string
}

variable "repo_url" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/YeelaLessick/MichalSelaChatBot"
}

variable "repo_branch" {
  description = "GitHub repository branch"
  type        = string
  default     = "main"
}

# Azure OpenAI variables
variable "openai_account_name" {
  description = "Name of the Azure OpenAI account"
  type        = string
}

variable "openai_deployment_name" {
  description = "Name of the Azure OpenAI deployment"
  type        = string
}

variable "azure_openai_api_version" {
  description = "Azure OpenAI API version"
  type        = string
  default     = "2025-01-01-preview"
}

# PostgreSQL Flexible Server variables (replacement for Cosmos DB)
variable "postgres_server_name" {
  description = "Name of the PostgreSQL Flexible Server (must be globally unique)"
  type        = string
}

variable "postgres_location" {
  description = "Azure region for the Postgres server (Burstable B1ms is widely available; pick one with capacity)"
  type        = string
  default     = "westeurope"
}

variable "postgres_database_name" {
  description = "Name of the application database"
  type        = string
  default     = "chatbot"
}

variable "postgres_sku_name" {
  description = "Compute SKU. B_Standard_B1ms ~ $13/mo."
  type        = string
  default     = "B_Standard_B1ms"
}

variable "postgres_storage_mb" {
  description = "Storage in MB (min 32768)"
  type        = number
  default     = 32768
}

variable "postgres_zone" {
  description = "Availability zone for the server (1/2/3 or null)"
  type        = string
  default     = null
}

variable "postgres_entra_admin_object_id" {
  description = "Entra user object ID to make Postgres admin (for psql/dashboard access). Optional."
  type        = string
  default     = ""
}

variable "postgres_entra_admin_principal_name" {
  description = "UPN of the Entra admin user"
  type        = string
  default     = ""
}

variable "postgres_firewall_rules" {
  description = "Extra firewall rules for the Postgres server: map of name -> { start_ip, end_ip }"
  type = map(object({
    start_ip = string
    end_ip   = string
  }))
  default = {}
}

# Communication Service variables
variable "communication_service_name" {
  description = "Name of the Communication Service"
  type        = string
}

variable "communication_data_location" {
  description = "Data location for Communication Service"
  type        = string
  default     = "Europe"
}

# Virtual Network variables
variable "vnet_name" {
  description = "Name of the virtual network"
  type        = string
}

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
}

variable "subnet_address_prefixes" {
  description = "Address prefixes for the subnet"
  type        = list(string)
}

variable "subnet_service_endpoints" {
  description = "Service endpoints for the subnet"
  type        = list(string)
  default     = null
}

# Managed Identity variables
variable "app_service_identity_name" {
  description = "Name of the App Service managed identity"
  type        = string
}

variable "bot_identity_name" {
  description = "Name of the Bot managed identity"
  type        = string
}

variable "openai_identity_name" {
  description = "Name of the OpenAI managed identity"
  type        = string
}

# Weekly summary email settings (App Service app settings)
variable "weekly_summary_enabled" {
  description = "Enable weekly summary scheduler (auto-disabled if SMTP settings are missing)"
  type        = bool
  default     = true
}

variable "weekly_summary_recipient" {
  description = "Recipient email for weekly summary"
  type        = string
  default     = "michalsela@info.com"
}

variable "weekly_summary_timezone" {
  description = "IANA timezone used by the weekly summary scheduler"
  type        = string
  default     = "Asia/Jerusalem"
}

variable "weekly_summary_send_hour" {
  description = "Weekly summary send hour (0-23)"
  type        = number
  default     = 9
}

variable "smtp_server" {
  description = "SMTP host"
  type        = string
  default     = null
}

variable "smtp_port" {
  description = "SMTP port"
  type        = number
  default     = 587
}

variable "smtp_username" {
  description = "SMTP username"
  type        = string
  default     = null
}

variable "smtp_password" {
  description = "SMTP password"
  type        = string
  sensitive   = true
  default     = null
}

variable "smtp_from" {
  description = "From email address"
  type        = string
  default     = null
}

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
