variable "storage_account_name" {
  description = "The name of the Storage Account"
  type        = string
}

variable "location" {
  description = "The location of the Storage Account"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the Resource Group"
  type        = string
}

variable "account_tier" {
  description = "The performance tier of the storage account (Standard or Premium)"
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "The replication strategy for the storage account"
  type        = string
  default     = "LRS"
}

variable "account_kind" {
  description = "The kind of the storage account (Storage, StorageV2, or BlobStorage)"
  type        = string
  default     = "StorageV2"
}

variable "access_tier" {
  description = "The access tier for the storage account (Hot or Cool)"
  type        = string
  default     = "Hot"
}

variable "enable_https_traffic_only" {
  description = "Enforce HTTPS traffic only"
  type        = bool
  default     = true
}

variable "min_tls_version" {
  description = "The minimum TLS version for the storage account"
  type        = string
  default     = "TLS1_2"
}

variable "change_feed_enabled" {
  description = "Enable change feed for blob storage"
  type        = bool
  default     = false
}

variable "container_delete_retention_days" {
  description = "Retention period for deleted containers"
  type        = number
  default     = 7
}

variable "blob_delete_retention_days" {
  description = "Retention period for deleted blobs"
  type        = number
  default     = 7
}

variable "permanent_delete_enabled" {
  description = "Enable permanent delete for blobs"
  type        = bool
  default     = false
}

variable "last_access_time_enabled" {
  description = "Enable last access time tracking for blobs"
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Enable versioning for blobs"
  type        = bool
  default     = false
}

variable "queue_hour_metrics_enabled" {
  description = "Enable hourly metrics for the queue service"
  type        = bool
  default     = true
}

variable "queue_hour_metrics_include_apis" {
  description = "Include API calls in hourly metrics"
  type        = bool
  default     = true
}

variable "queue_hour_metrics_retention_days" {
  description = "Retention period for hourly metrics"
  type        = number
  default     = 7
}

variable "queue_logging_delete" {
  description = "Enable logging for delete operations"
  type        = bool
  default     = false
}

variable "queue_logging_read" {
  description = "Enable logging for read operations"
  type        = bool
  default     = false
}

variable "queue_logging_write" {
  description = "Enable logging for write operations"
  type        = bool
  default     = false
}

variable "queue_logging_retention_days" {
  description = "Retention period for queue logs"
  type        = number
  default     = 0
}

variable "share_retention_days" {
  description = "Retention period for share properties"
  type        = number
  default     = 7
}