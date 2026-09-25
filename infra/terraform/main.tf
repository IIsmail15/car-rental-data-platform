terraform {
  required_version = ">= 1.6.0"
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}
