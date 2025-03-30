# Private DNS Zone Variables
variable "private_dns_zone_name" {
  description = "The name of the private DNS zone"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

# SOA Record Variables
variable "soa_email" {
  description = "Email for the SOA record"
  type        = string
  default     = "azureprivatedns-host.microsoft.com"
}

variable "soa_expire_time" {
  description = "Expire time for the SOA record"
  type        = number
  default     = 2419200
}

variable "soa_minimum_ttl" {
  description = "Minimum TTL for the SOA record"
  type        = number
  default     = 10
}

variable "soa_refresh_time" {
  description = "Refresh time for the SOA record"
  type        = number
  default     = 3600
}

variable "soa_retry_time" {
  description = "Retry time for the SOA record"
  type        = number
  default     = 300
}

variable "soa_ttl" {
  description = "TTL for the SOA record"
  type        = number
  default     = 3600
}

# VNet Link Variables
variable "dns_zone_vnet_link_name" {
  description = "The name of the virtual network link to the DNS zone"
  type        = string
}

variable "virtual_network_id" {
  description = "The ID of the virtual network"
  type        = string
}

variable "registration_enabled" {
  description = "Whether registration is enabled for the VNet link"
  type        = bool
  default     = false
}
