resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  location                 = var.location
  resource_group_name      = var.resource_group_name
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  account_kind             = var.account_kind
  access_tier              = var.access_tier
  min_tls_version          = var.min_tls_version

  blob_properties {
    change_feed_enabled = var.change_feed_enabled

    container_delete_retention_policy {
      days = var.container_delete_retention_days
    }

    delete_retention_policy {
      days                     = var.blob_delete_retention_days
      permanent_delete_enabled = var.permanent_delete_enabled
    }

    last_access_time_enabled = var.last_access_time_enabled
    versioning_enabled       = var.versioning_enabled
  }

  share_properties {
    retention_policy {
      days = var.share_retention_days
    }
  }
}
