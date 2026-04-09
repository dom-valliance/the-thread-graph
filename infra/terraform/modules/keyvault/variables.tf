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

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "aks_identity_id" {
  description = "Object ID of the AKS kubelet identity"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
