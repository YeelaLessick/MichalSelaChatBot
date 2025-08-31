resource "azurerm_cosmosdb_account" "main" {
  name                = var.cosmosdb_name
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  automatic_failover_enabled   = true
  free_tier_enabled           = var.enable_free_tier
  analytical_storage_enabled  = true

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = var.location
    failover_priority = 0
    zone_redundant    = false
  }

  backup {
    type                = "Periodic"
    interval_in_minutes = 720
    retention_in_hours  = 24
    storage_redundancy  = "Local"
  }

  ip_range_filter = var.ip_range_filter

  tags = var.tags
}
