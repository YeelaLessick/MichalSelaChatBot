provider "azurerm" {
  features {}
  subscription_id = "acd75acf-314c-435d-b215-b212f1586640"
  skip_provider_registration = true
}

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.117.0"
    }
  }
}
