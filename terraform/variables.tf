# Variables for the Job Skills Analyzer infrastructure

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "job-skills-analyzer"
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "624943535027"
}

variable "email_address" {
  description = "Email address for SNS notifications"
  type        = string
  default     = "ignacio.baratech@alumni.esade.edu"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "lambda_memory" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 512
}

variable "api_key" {
  description = "API key for authentication"
  type        = string
  default     = "job-skills-analyzer-secret-key-2024"
  sensitive   = true
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  default     = "dev"
}
