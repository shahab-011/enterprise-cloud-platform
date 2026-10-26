terraform {
  required_version = ">= 1.5.0"
}

locals {
  resource_prefix = "${var.project_name}-${var.environment}"
  application = {
    name        = local.resource_prefix
    namespace   = var.kubernetes_namespace
    image       = var.container_image
    replicas    = var.replicas
    environment = var.environment
  }
}

output "application_plan" {
  description = "Illustrative application metadata only; this configuration creates no resources."
  value       = local.application
}
