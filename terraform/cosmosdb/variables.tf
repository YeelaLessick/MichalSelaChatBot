variable "cosmosdb_name" {
  description = "Name of the Cosmos DB account"
  type        = string
}

variable "database_name" {
  description = "Name of the Cosmos DB SQL database"
  type        = string
  default     = "chatbot"
}

variable "container_name" {
  description = "Name of the Cosmos DB SQL container"
  type        = string
  default     = "conversations"
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "enable_free_tier" {
  description = "Enable Cosmos DB free tier"
  type        = bool
  default     = false
}

variable "ip_range_filter" {
  description = "IP range filter for Cosmos DB"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to Cosmos DB resources"
  type        = map(string)
  default     = {}
}
