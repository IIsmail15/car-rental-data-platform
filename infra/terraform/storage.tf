resource "azurerm_storage_account" "data_lake" {
  name                            = "st${var.project_name}${var.environment}"
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  is_hns_enabled                  = true
  allow_nested_items_to_be_public = false


  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}
resource "azurerm_storage_data_lake_gen2_filesystem" "raw" {
  name               = "raw"
  storage_account_id = azurerm_storage_account.data_lake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "curated" {
  name               = "curated"
  storage_account_id = azurerm_storage_account.data_lake.id
}