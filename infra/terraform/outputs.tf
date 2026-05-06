output "vm_public_ip" {
  description = "Public IP of the app server"
  value       = azurerm_public_ip.app.ip_address
}

output "vm_admin_username" {
  description = "Admin username for SSH"
  value       = var.admin_username
}

output "db_host" {
  description = "PostgreSQL server hostname"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "db_name" {
  description = "Database name"
  value       = azurerm_postgresql_flexible_server_database.app.name
}

output "ssh_command" {
  description = "SSH command to connect to the VM"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.app.ip_address}"
}
