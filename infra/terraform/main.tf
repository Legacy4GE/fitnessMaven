terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.0"
}

provider "azurerm" {
  features {}
  subscription_id = "186a5b6e-e090-4837-8f7e-4565f8a4e204"
}

# --- Resource Group ---
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# --- Networking ---
resource "azurerm_virtual_network" "main" {
  name                = "vnet-fitnessmaven"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "app" {
  name                 = "subnet-app"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "db" {
  name                 = "subnet-db"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "postgresql-delegation"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

# --- Network Security Group ---
resource "azurerm_network_security_group" "app" {
  name                = "nsg-fitnessmaven-app"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowSSH"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAPI"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}

# --- Public IP ---
resource "azurerm_public_ip" "app" {
  name                = "pip-fitnessmaven"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# --- Network Interface ---
resource "azurerm_network_interface" "app" {
  name                = "nic-fitnessmaven"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.app.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.app.id
  }
}

# --- Virtual Machine (Ubuntu 22.04 LTS) ---
resource "azurerm_linux_virtual_machine" "app" {
  name                            = "vm-fitnessmaven"
  location                        = azurerm_resource_group.main.location
  resource_group_name             = azurerm_resource_group.main.name
  size                            = var.vm_size
  admin_username                  = var.admin_username
  disable_password_authentication = true

  network_interface_ids = [azurerm_network_interface.app.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.ssh_public_key_path)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
}

# --- Private DNS Zone for PostgreSQL ---
resource "azurerm_private_dns_zone" "db" {
  name                = "fitnessmaven.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "db" {
  name                  = "fitnessmaven-db-link"
  private_dns_zone_name = azurerm_private_dns_zone.db.name
  resource_group_name   = azurerm_resource_group.main.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

# --- PostgreSQL Flexible Server ---
resource "azurerm_postgresql_flexible_server" "main" {
  name                          = "psql-fitnessmaven"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  version                       = "15"
  administrator_login           = var.db_admin_username
  administrator_password        = var.db_admin_password
  storage_mb                    = 32768
  sku_name                      = "B_Standard_B1ms"
  delegated_subnet_id           = azurerm_subnet.db.id
  private_dns_zone_id           = azurerm_private_dns_zone.db.id
  public_network_access_enabled = false

  depends_on = [azurerm_private_dns_zone_virtual_network_link.db]
}

resource "azurerm_postgresql_flexible_server_database" "app" {
  name      = "fitnessmaven"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}
