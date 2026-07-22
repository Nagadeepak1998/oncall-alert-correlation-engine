output "labels" {
  description = "Labels that a platform team could attach to alerts, dashboards, or deployments."
  value       = local.labels
}

output "service_registration" {
  description = "Local-only service registration metadata for platform catalog review."
  value       = terraform_data.service_registration.output
}
