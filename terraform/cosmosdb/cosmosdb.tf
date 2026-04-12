# Cosmos DB Account
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

# Cosmos DB SQL Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.database_name
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
  
  # Throughput - use autoscale or manual
  throughput          = var.enable_free_tier ? null : 400
}

# Cosmos DB SQL Container for Conversations
resource "azurerm_cosmosdb_sql_container" "conversations" {
  name                = var.container_name
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  
  # Partition key on /id (standard Cosmos DB practice)
  partition_key_paths = ["/id"]
  partition_key_version = 2
  
  # Throughput - inherit from database if set, otherwise use container-level
  throughput          = null
  
  # Indexing policy for optimal queries
  indexing_policy {
    indexing_mode = "consistent"
    
    included_path {
      path = "/*"
    }
    
    # Exclude large conversation arrays from indexing to save RU costs
    excluded_path {
      path = "/Conversation/*"
    }
    
    # Include specific extraction fields for querying
    included_path {
      path = "/Extraction/extracted_fields/conversation_time/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/inquiry_subject/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/caller_age/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/caller_gender/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/relationship_to_threat/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/referred_to/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/contacted_referral/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/received_good_response/?"
    }
    
    included_path {
      path = "/Extraction/extracted_fields/wants_human_callback/?"
    }
    
    included_path {
      path = "/Metadata/?"
    }
  }
  
  # TTL disabled (conversations stored indefinitely)
  default_ttl = null
}
