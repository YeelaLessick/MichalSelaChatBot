variable "bot_name" {
  description = "Name of the Azure Bot Service"
  type        = string
  default = "michalSelaBot"
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "sku" {
  description = "SKU of the Azure Bot Service"
  type        = string
  default     = "F0" # Options: F0 (free) or S1 (standard)
}