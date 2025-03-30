resource "azurerm_private_dns_zone" "main" {
  name                = var.private_dns_zone_name
  resource_group_name = var.resource_group_name

  soa_record {
    email        = var.soa_email
    expire_time  = var.soa_expire_time
    minimum_ttl  = var.soa_minimum_ttl
    refresh_time = var.soa_refresh_time
    retry_time   = var.soa_retry_time
    ttl          = var.soa_ttl
  }
}
