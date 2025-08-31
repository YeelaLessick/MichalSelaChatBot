resource "azurerm_communication_service" "main" {
  name                = var.communication_service_name
  resource_group_name = var.resource_group_name
  data_location       = var.data_location

  tags = var.tags
}
