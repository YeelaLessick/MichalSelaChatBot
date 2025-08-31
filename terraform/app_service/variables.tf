variable "resource_group_name" {
  description = "Name of the Resource Group"
  type        = string
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
  default     = "westeurope"
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = "michalsela-app-service-plan"
}

variable "app_service_name" {
  description = "Name of the App Service"
  type        = string
}

variable "sku_name" {
  description = "The SKU name for the App Service Plan"
  type        = string
  default     = "B1"
}

variable "microsoft_app_id" {
  description = "Microsoft App ID for authentication"
  type        = string
  default     = null
}

variable "microsoft_app_tenant_id" {
  description = "Tenant ID of the Microsoft App"
  type        = string
  default     = null
}

variable "linux_fx_version" {
  description = "Linux runtime stack for the App Service"
  type        = string
  default     = "PYTHON|3.12"
}

variable "always_on" {
  description = "Should the app be always on"
  type        = bool
  default     = false
}

variable "public_network_access_enabled" {
  description = "Should public network access be enabled"
  type        = bool
  default     = true
}

variable "virtual_network_subnet_id" {
  description = "ID of the subnet to integrate the app service with"
  type        = string
  default     = null
}

variable "vnet_route_all_enabled" {
  description = "Should all traffic be routed through the VNet"
  type        = bool
  default     = true
}

variable "scm_type" {
  description = "Type of Source Control Management"
  type        = string
  default     = "GitHubAction"
}

variable "http_logs_retention_mb" {
  description = "HTTP logs retention in MB"
  type        = number
  default     = 35
}

variable "additional_app_settings" {
  description = "Additional app settings for the web app"
  type        = map(string)
  default     = {}
}

variable "repo_url" {
  description = "Repository URL for source control"
  type        = string
  default     = null
}

variable "repo_branch" {
  description = "Branch name for source control"
  type        = string
  default     = "main"
}

# Azure OpenAI Configuration
variable "azure_openai_api_key" {
  description = "Azure OpenAI API key"
  type        = string
  sensitive   = true
  default     = null
}

variable "azure_openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  type        = string
  default     = null
}

variable "azure_openai_api_version" {
  description = "Azure OpenAI API version"
  type        = string
  default     = "2024-02-01"
}

variable "azure_openai_deployment_name" {
  description = "Azure OpenAI deployment name"
  type        = string
  default     = null
}
