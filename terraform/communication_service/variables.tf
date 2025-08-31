variable "communication_service_name" {
  description = "Name of the Communication Service"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "data_location" {
  description = "The data location for the Communication Service"
  type        = string
  default     = "Europe"
}

variable "tags" {
  description = "Tags to apply to Communication Service resources"
  type        = map(string)
  default     = {}
}
