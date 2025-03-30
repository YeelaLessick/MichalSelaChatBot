variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "virtual_network_name" {
  description = "Name of the virtual network"
  type        = string
}

variable "subnet1_name" {
  description = "Name of the first subnet"
  type        = string
}

variable "subnet1_address_prefixes" {
  description = "Address prefixes for the first subnet"
  type        = list(string)
}

variable "subnet2_name" {
  description = "Name of the second subnet"
  type        = string
}

variable "subnet2_address_prefixes" {
  description = "Address prefixes for the second subnet"
  type        = list(string)
}

variable "subnet2_service_endpoints" {
  description = "Service endpoints for the second subnet"
  type        = list(string)
  default     = []
}

variable "default_outbound_access_enabled" {
  description = "Enable default outbound access"
  type        = bool
  default     = true
}

variable "enforce_private_link_endpoint_network_policies" {
  description = "Enforce private link endpoint network policies"
  type        = bool
  default     = true
}

variable "enforce_private_link_service_network_policies" {
  description = "Enforce private link service network policies"
  type        = bool
  default     = false
}

variable "private_endpoint_network_policies_enabled" {
  description = "Enable private endpoint network policies"
  type        = bool
  default     = false
}

variable "private_link_service_network_policies_enabled" {
  description = "Enable private link service network policies"
  type        = bool
  default     = true
}
