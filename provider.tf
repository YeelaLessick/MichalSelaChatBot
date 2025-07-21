terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # Specify the version, adjust if needed
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.40.0" # Replace with the latest version
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "acd75acf-314c-435d-b215-b212f1586640"
}
