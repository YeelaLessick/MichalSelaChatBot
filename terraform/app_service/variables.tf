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
  default = "michalsela-app-service-plan"
}

variable "app_service_name" {
  description = "Name of the App Service"
  type        = string
}

variable "identity_type" {
  description = "The type of identity to assign to the App Service"
  type        = string
  default     = "SystemAssigned, UserAssigned"
}

variable "microsoft_app_id" {
  description = "Microsoft App ID for authentication"
  type        = string
}

variable "microsoft_app_tenant_id" {
  description = "Tenant ID of the Microsoft App"
  type        = string
}

variable "linux_fx_version" {
  description = "Linux runtime stack for the App Service"
  type        = string
  default     = "PYTHON|3.12"
}

variable "repo_url" {
  description = "Repository URL for source control"
  type        = string
}

variable "repo_branch" {
  description = "Branch name for source control"
  type        = string
  default     = "main"
}