variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "Sweden Central"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "carrental"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "postgres_admin_username" {
  description = "Administrator username for PostgreSQL Flexible Server"
  type        = string
}

variable "postgres_admin_password" {
  description = "Administrator password for PostgreSQL Flexible Server"
  type        = string
  sensitive   = true
}