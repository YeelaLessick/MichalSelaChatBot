output "openai_resource_id" {
  description = "The ID of the Azure OpenAI resource"
  value       = azurerm_cognitive_account.openai.id
}

output "openai_account_name" {
  description = "The name of the Azure OpenAI resource"
  value       = azurerm_cognitive_account.openai.name
}

output "gpt4_deployment_name" {
  description = "The name of the GPT-4 deployment"
  value       = var.deployment_name
}