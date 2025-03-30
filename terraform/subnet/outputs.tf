output "subnet1_id" {
  description = "The ID of the first subnet"
  value       = azurerm_subnet.subnet1.id
}

output "subnet1_name" {
  description = "The name of the first subnet"
  value       = azurerm_subnet.subnet1.name
}

output "subnet2_id" {
  description = "The ID of the second subnet"
  value       = azurerm_subnet.subnet2.id
}

output "subnet2_name" {
  description = "The name of the second subnet"
  value       = azurerm_subnet.subnet2.name
}
