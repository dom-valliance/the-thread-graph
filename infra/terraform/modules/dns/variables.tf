variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "domain_name" {
  description = "Custom domain name"
  type        = string
}

variable "public_ip_id" {
  description = "Public IP resource ID for A record (optional)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
