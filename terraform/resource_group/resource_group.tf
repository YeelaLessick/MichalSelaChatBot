resource "azurerm_resource_group" "main" {
  location = var.location
  name     = var.resource_group_name
}