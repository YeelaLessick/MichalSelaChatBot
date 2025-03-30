# Azure OpenAI Account
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_account_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"
}

# ARM Template for OpenAI Deployment
resource "azurerm_resource_group_template_deployment" "openai_deployment" {
  name                = "openai-deployment"
  resource_group_name = var.resource_group_name
  deployment_mode     = "Incremental"

  template_content = <<EOF
  {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "resources": [
      {
        "type": "Microsoft.CognitiveServices/accounts/deployments",
        "apiVersion": "2023-01-01",
        "name": "${var.deployment_name}",
        "properties": {
          "model": "gpt-4-32k-mini",
          "scaleSettings": {
            "scaleType": "Standard"
          }
        }
      }
    ]
  }
  EOF

  parameters_content = jsonencode({})
}
