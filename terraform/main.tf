# module "resource_group" {
#   source = "./resource_group"

#   location            = var.location
#   resource_group_name = var.resource_group_name
# }

# module "storage_account" {
#   source = "./storage_account"

#   storage_account_name     = "mihcalseladata"          # The name of the storage account
#   location                 = var.location              # Use a variable for location
#   resource_group_name      = var.resource_group_name # Reference the resource group module
#   account_tier             = "Standard"               # Storage account tier
#   account_replication_type = "LRS"                    # Replication type
#   account_kind             = "StorageV2"              # Account kind (e.g., StorageV2)
#   access_tier              = "Hot"                    # Access tier (Hot or Cool)
# }

module "storage_container" {
  source = "./storage_container"

  container_name                 = "data"
  storage_account_name           = module.storage_account.storage_account_name # Reference from the storage account module
}

module "virtual_network" {
  source = "./virtual_network"

  vnet_name                = "vnet-sjsvtepn"
  location                 = var.location
  resource_group_name      = var.resource_group_name # Reference the resource group module
  address_space            = ["10.0.0.0/16"]
}


module "private_dns" {
  source = "./private_dns"

  private_dns_zone_name   = "privatelink.mongo.cosmos.azure.com"
  resource_group_name     = var.resource_group_name
  dns_zone_vnet_link_name = "link-biwvnsgqc6gp4"
  virtual_network_id      = module.virtual_network.vnet_id
}

module "subnet" {
  source = "./subnet"

  resource_group_name                            = var.resource_group_name
  virtual_network_name                           = module.virtual_network.vnet_name
  subnet1_name                                   = "subnet-biwvnsgqc6gp4"
  subnet1_address_prefixes                       = ["10.0.2.0/24"]
  subnet2_name                                   = "subnet-tvektdbl"
  subnet2_address_prefixes                       = ["10.0.1.0/24"]
  subnet2_service_endpoints                      = ["Microsoft.Storage"]
}

# module "azure_bot" {
#   source = "./azure_bot"
#   
#   bot_name            = "michalselabot"
#   location            = var.location
#   sku                 = "F0"
#   resource_group_name = var.resource_group_name
# }

# module "azure_openai" {
#   source              = "./azure_openai"

#   openai_account_name = "michalsela-openai"
#   deployment_name     = "gpt4o1-mini-deployment"
#   location            = var.location
#   resource_group_name = var.resource_group_name
# }

# module "app_service" {
#   source                = "./app_service"

#   app_service_name      = "michalchatbotwebapp"
#   location              = var.location
#   resource_group_name   = var.resource_group_name
#   microsoft_app_id            = module.azure_bot.app_id       # Reuse Bot's App ID
#   microsoft_app_tenant_id         = module.azure_bot.tenant_id    # Reuse Bot's Tenant ID
#   repo_url              = "https://github.com/YeelaLessick/MichalSelaChatBot"
# }
