variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "rg-fitnessmaven"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "vm_size" {
  description = "Size of the VM"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "fitnessmaven"
}

variable "db_admin_username" {
  description = "Admin username for PostgreSQL"
  type        = string
  default     = "fmadmin"
}

variable "db_admin_password" {
  description = "Admin password for PostgreSQL"
  type        = string
  sensitive   = true
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key for VM access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
