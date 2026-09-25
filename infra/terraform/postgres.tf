resource "azurerm_postgresql_flexible_server" "main" {
  name                = "psql-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password

  sku_name   = "B_Standard_B1ms"
  version    = "16"
  storage_mb = 32768

  lifecycle {
    ignore_changes = [
      zone
    ]
  }

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}
resource "azurerm_postgresql_flexible_server_database" "car_rental" {
  name      = "car_rental"
  server_id = azurerm_postgresql_flexible_server.main.id
}
