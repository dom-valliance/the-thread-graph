variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "acr_sku" {
  description = "SKU for the container registry"
  type        = string
  default     = "Standard"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
