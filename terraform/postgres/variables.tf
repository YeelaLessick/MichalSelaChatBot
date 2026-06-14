variable "server_name" {
  description = "Name of the PostgreSQL Flexible Server (must be globally unique)"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group to create the server in"
  type        = string
}

variable "location" {
  description = "Azure region (must support Flexible Server + Burstable tier)"
  type        = string
}

variable "tenant_id" {
  description = "Entra tenant ID for AAD authentication"
  type        = string
}

variable "database_name" {
  description = "Name of the application database"
  type        = string
  default     = "chatbot"
}

variable "postgres_version" {
  description = "PostgreSQL major version"
  type        = string
  default     = "16"
}

variable "sku_name" {
  description = "Compute SKU. B_Standard_B1ms = 1 vCPU / 2 GB (~$13/mo)."
  type        = string
  default     = "B_Standard_B1ms"
}

variable "storage_mb" {
  description = "Storage size in MB. Min 32768 (32 GB)."
  type        = number
  default     = 32768
}

variable "backup_retention_days" {
  description = "Backup retention (7-35 days)"
  type        = number
  default     = 7
}

variable "zone" {
  description = "Availability zone (1/2/3). null lets Azure choose."
  type        = string
  default     = null
}

variable "enable_password_auth" {
  description = "Allow password-based admin login alongside Entra ID"
  type        = bool
  default     = false
}

variable "admin_login" {
  description = "Password admin login name (only used if enable_password_auth)"
  type        = string
  default     = "pgadmin"
}

variable "admin_password" {
  description = "Password admin password (only used if enable_password_auth)"
  type        = string
  default     = null
  sensitive   = true
}

variable "app_service_identity_principal_id" {
  description = "Object (principal) ID of the App Service managed identity. Will be granted Entra admin on the server."
  type        = string
  default     = ""
}

variable "app_service_identity_name" {
  description = "Name of the App Service managed identity (used as principal_name in Entra admin record)"
  type        = string
  default     = ""
}

variable "entra_admin_object_id" {
  description = "Object ID of an Entra user to make admin (for psql access / dashboard). Optional."
  type        = string
  default     = ""
}

variable "entra_admin_principal_name" {
  description = "UPN of the Entra admin user"
  type        = string
  default     = ""
}

variable "firewall_rules" {
  description = "Extra firewall rules: map of name -> { start_ip, end_ip }"
  type = map(object({
    start_ip = string
    end_ip   = string
  }))
  default = {}
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}
