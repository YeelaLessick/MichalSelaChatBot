variable "openai_account_name" {
  description = "Name of the Azure OpenAI resource"
  type        = string
}

variable "deployment_name" {
  description = "Name of the GPT-4 deployment"
  type        = string
}

variable "location" {
  description = "Location of the Azure OpenAI resource"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group where the Azure OpenAI resource will be created"
  type        = string
}