environment         = "dev"
location            = "uksouth"
resource_group_name = "rg-valliance-graph-dev"

kubernetes_version  = "1.29"
system_node_count   = 1
system_node_vm_size = "Standard_D2s_v3"
user_node_count     = 2
user_node_vm_size   = "Standard_D2s_v3"

acr_sku     = "Standard"
domain_name = "dev.graph.valliance.dev"
