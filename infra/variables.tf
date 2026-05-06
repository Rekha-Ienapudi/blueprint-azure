variable "usecase" {
  description = "Usecase name"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.usecase))
    error_message = "usecase must be 3–20 chars, lowercase alphanumeric or hyphens."
  }
}

variable "env" {
  description = "Environment"
  type        = string

  validation {
    condition     = contains(["dev", "test", "stage", "prod"], var.env)
    error_message = "env must be one of: dev, test, stage, prod."
  }
}

variable "owner" {
  description = "Owner"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.owner))
    error_message = "owner must be 3–20 chars, lowercase alphanumeric or hyphens."
  }
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "image_name" {
  description = "Docker image name"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-_]{3,50}$", var.image_name))
    error_message = "image_name must be 3–50 chars, lowercase alphanumeric, hyphens, or underscores."
  }
}

variable "tags" {
  description = "Standard tags for all resources"
  type = map(string)

  validation {
    condition     = alltrue([for k, v in var.tags : length(v) > 0])
    error_message = "All tags must have non-empty values."
  }
}
