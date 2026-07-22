variable "service_name" {
  type        = string
  description = "Service name used for generated ownership metadata."
  default     = "oncall-alert-correlation-engine"
}

variable "environment" {
  type        = string
  description = "Target environment label for generated metadata."
  default     = "local"
}

