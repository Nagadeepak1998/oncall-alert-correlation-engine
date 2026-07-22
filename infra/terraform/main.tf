terraform {
  required_version = ">= 1.6.0"
}

variable "service_name" {
  type        = string
  description = "Logical service name used for platform catalog wiring."
  default     = "oncall-alert-correlation-engine"
}

variable "owner" {
  type        = string
  description = "Owning team for the service registration."
  default     = "platform-reliability"
}

resource "terraform_data" "service_registration" {
  input = {
    service_name     = var.service_name
    owner            = var.owner
    runtime          = "fastapi"
    metrics_endpoint = "/metrics"
    runbook_required = true
  }
}

output "service_registration" {
  value = terraform_data.service_registration.output
}

