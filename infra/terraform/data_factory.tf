resource "azurerm_data_factory" "main" {
  name                = "adf-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}