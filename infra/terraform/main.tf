locals {
  labels = {
    service     = var.service_name
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
  }
}

resource "terraform_data" "service_registration" {
  input = {
    service_name     = var.service_name
    owner            = var.owner
    environment      = var.environment
    runtime          = "fastapi"
    metrics_endpoint = "/metrics"
    runbook_required = true
  }
}
