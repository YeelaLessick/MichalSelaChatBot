resource "azurerm_subnet" "subnet1" {
  name                                           = var.subnet1_name
  resource_group_name                            = var.resource_group_name
  virtual_network_name                           = var.virtual_network_name
  address_prefixes                               = var.subnet1_address_prefixes
  default_outbound_access_enabled                = var.default_outbound_access_enabled
  private_link_service_network_policies_enabled  = var.private_link_service_network_policies_enabled
}

resource "azurerm_subnet" "subnet2" {
  name                                           = var.subnet2_name
  resource_group_name                            = var.resource_group_name
  virtual_network_name                           = var.virtual_network_name
  address_prefixes                               = var.subnet2_address_prefixes
  default_outbound_access_enabled                = var.default_outbound_access_enabled
  private_link_service_network_policies_enabled  = var.private_link_service_network_policies_enabled
  service_endpoints                              = var.subnet2_service_endpoints

  delegation {
    name = "delegation"

    service_delegation {
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
      name    = "Microsoft.Web/serverFarms"
    }
  }
}
