variable "container_name" {
  description = "The name of the storage container"
  type        = string
}

variable "storage_account_name" {
  description = "The name of the storage account where the container is created"
  type        = string
}

variable "container_access_type" {
  description = "The access type for the storage container (e.g., private, blob, container)"
  type        = string
  default     = "private"
}
