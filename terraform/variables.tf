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
  default     = "223280412524"
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
  default     = 256
}
