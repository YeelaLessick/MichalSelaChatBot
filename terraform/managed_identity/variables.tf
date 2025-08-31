variable "identity_name" {
  description = "The name of the managed identity"
  type        = string
}

variable "location" {
  description = "The location of the managed identity"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the managed identity"
  type        = map(string)
  default     = {}
}
