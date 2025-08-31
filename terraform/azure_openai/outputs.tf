output "openai_resource_id" {
  description = "The ID of the Azure OpenAI resource"
  value       = azurerm_cognitive_account.openai.id
}

output "openai_account_name" {
  description = "The name of the Azure OpenAI resource"
  value       = azurerm_cognitive_account.openai.name
}

output "openai_api_key" {
  description = "The primary API key for the Azure OpenAI resource"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "openai_endpoint" {
  description = "The endpoint URL for the Azure OpenAI resource"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "gpt4_deployment_name" {
  description = "The name of the GPT-4 deployment"
  value       = var.deployment_name
}
