resource "azurerm_virtual_network" "main" {
  name                    = var.vnet_name
  location                = var.location
  resource_group_name     = var.resource_group_name
  address_space           = var.address_space
  flow_timeout_in_minutes = var.flow_timeout_in_minutes
}
