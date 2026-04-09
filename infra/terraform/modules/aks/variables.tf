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

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
}

variable "system_node_count" {
  description = "Number of system pool nodes"
  type        = number
}

variable "system_node_vm_size" {
  description = "VM size for system pool"
  type        = string
}

variable "user_node_count" {
  description = "Number of user pool nodes"
  type        = number
}

variable "user_node_vm_size" {
  description = "VM size for user pool"
  type        = string
}

variable "vnet_subnet_id" {
  description = "Subnet ID for AKS nodes"
  type        = string
}

variable "pod_subnet_id" {
  description = "Subnet ID for AKS pods"
  type        = string
}

variable "acr_id" {
  description = "ACR resource ID for pull access"
  type        = string
}

variable "log_analytics_id" {
  description = "Log Analytics workspace ID"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
