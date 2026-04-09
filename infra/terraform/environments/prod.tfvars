environment         = "prod"
location            = "uksouth"
resource_group_name = "rg-valliance-graph-prod"

kubernetes_version  = "1.29"
system_node_count   = 3
system_node_vm_size = "Standard_D2s_v3"
user_node_count     = 5
user_node_vm_size   = "Standard_D4s_v3"

acr_sku     = "Premium"
domain_name = "graph.valliance.dev"
