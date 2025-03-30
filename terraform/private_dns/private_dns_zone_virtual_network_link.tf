resource "azurerm_private_dns_zone_virtual_network_link" "main" {
  name                  = var.dns_zone_vnet_link_name
  private_dns_zone_name = var.private_dns_zone_name
  resource_group_name   = var.resource_group_name
  virtual_network_id    = var.virtual_network_id
  registration_enabled  = var.registration_enabled
}
