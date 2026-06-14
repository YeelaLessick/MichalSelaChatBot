# =============================================================================
# Azure Database for PostgreSQL - Flexible Server
# =============================================================================
# Replaces Cosmos DB for storing chatbot conversations and extractions.
#
# Cost model: Burstable B1ms (~$13-18/month) vs. Cosmos DB (~$1,200/month)
# Storage:    32 GB SSD, plenty for JSONB conversation history
# Auth:       Microsoft Entra ID (passwordless) - uses managed identity from
#             App Service to fetch a short-lived token at runtime.
# =============================================================================

# Public access mode (no VNet integration) -- App Service connects through
# Postgres firewall rules. For private VNet access set
# var.delegated_subnet_id and var.private_dns_zone_id and enable the
# corresponding fields below.

resource "azurerm_postgresql_flexible_server" "main" {
  name                = var.server_name
  resource_group_name = var.resource_group_name
  location            = var.location

  version    = var.postgres_version
  sku_name   = var.sku_name        # e.g. "B_Standard_B1ms"
  storage_mb = var.storage_mb      # min 32768 (32 GB) for Burstable

  # Use Entra-only authentication (no admin password stored anywhere)
  authentication {
    active_directory_auth_enabled = true
    password_auth_enabled         = var.enable_password_auth
    tenant_id                     = var.tenant_id
  }

  backup_retention_days        = var.backup_retention_days
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  # Zone left null -> Azure picks a zone in the region
  zone = var.zone

  # Only set password if password auth is enabled (otherwise omit)
  administrator_login    = var.enable_password_auth ? var.admin_login : null
  administrator_password = var.enable_password_auth ? var.admin_password : null

  tags = var.tags

  lifecycle {
    ignore_changes = [zone, high_availability]
  }
}

# Configure the App Service managed identity as an Entra admin so it can log in
resource "azurerm_postgresql_flexible_server_active_directory_administrator" "app_service" {
  # Use the identity *name* (known at plan time) for the count gate; the
  # principal_id is only known after apply but that's fine inside the resource.
  count = var.app_service_identity_name != "" ? 1 : 0

  server_name         = azurerm_postgresql_flexible_server.main.name
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  object_id           = var.app_service_identity_principal_id
  principal_name      = var.app_service_identity_name
  principal_type      = "ServicePrincipal"
}

# Optional: add a human admin (your Entra user) for dashboard/dev access
resource "azurerm_postgresql_flexible_server_active_directory_administrator" "user_admin" {
  count = var.entra_admin_object_id != "" ? 1 : 0

  server_name         = azurerm_postgresql_flexible_server.main.name
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  object_id           = var.entra_admin_object_id
  principal_name      = var.entra_admin_principal_name
  principal_type      = "User"
}

# Database for chatbot data
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"

  lifecycle {
    prevent_destroy = false
  }
}

# Firewall rule: allow Azure services (App Service outbound IPs)
# 0.0.0.0 / 0.0.0.0 is the documented sentinel for "Allow Azure resources"
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Optional: extra firewall rules (e.g. developer home IPs for psql)
resource "azurerm_postgresql_flexible_server_firewall_rule" "extra" {
  for_each = var.firewall_rules

  name             = each.key
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = each.value.start_ip
  end_ip_address   = each.value.end_ip
}

# Server parameters tuned for low-volume JSONB workload
resource "azurerm_postgresql_flexible_server_configuration" "require_secure_transport" {
  name      = "require_secure_transport"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "ON"
}
