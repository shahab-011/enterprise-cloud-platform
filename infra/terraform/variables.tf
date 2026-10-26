variable "project_name" {
  description = "Short lowercase project identifier."
  type        = string
  default     = "ecp"
}

variable "environment" {
  description = "Non-production environment name."
  type        = string
  default     = "demo"
}

variable "kubernetes_namespace" {
  description = "Namespace used by the separately reviewed Kubernetes manifests."
  type        = string
  default     = "ecp-demo"
}

variable "container_image" {
  description = "Image reference built and reviewed by the operator."
  type        = string
  default     = "enterprise-cloud-platform-demo:local"
}

variable "replicas" {
  description = "Illustrative desired replica count."
  type        = number
  default     = 1
}
