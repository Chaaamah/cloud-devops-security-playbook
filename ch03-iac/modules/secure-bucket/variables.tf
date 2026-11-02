variable "name" {
  description = "Globally unique bucket name."
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key used for default encryption."
  type        = string
}

variable "retention_days" {
  description = "Days before noncurrent object versions are deleted. 0 keeps them forever."
  type        = number
  default     = 0

  validation {
    condition     = var.retention_days >= 0
    error_message = "retention_days must be zero or positive."
  }
}

variable "tags" {
  description = "Tags; owner, environment and data_class are required."
  type        = map(string)

  validation {
    condition     = alltrue([for k in ["owner", "environment", "data_class"] : contains(keys(var.tags), k)])
    error_message = "tags must include owner, environment and data_class."
  }
}
