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

# Cosmos DB variables
variable "cosmosdb_name" {
  description = "Name of the Cosmos DB account"
  type        = string
}

variable "cosmosdb_enable_free_tier" {
  description = "Enable free tier for Cosmos DB"
  type        = bool
  default     = false
}

variable "cosmosdb_ip_range_filter" {
  description = "IP range filter for Cosmos DB"
  type        = string
  default     = ""
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

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
