# Outputs for Job Skills Analyzer infrastructure

output "s3_raw_bucket" {
  description = "Name of the raw data S3 bucket"
  value       = aws_s3_bucket.raw.id
}

output "s3_curated_bucket" {
  description = "Name of the curated data S3 bucket"
  value       = aws_s3_bucket.curated.id
}

output "s3_athena_results_bucket" {
  description = "Name of the Athena results S3 bucket"
  value       = aws_s3_bucket.athena_results.id
}

output "athena_database" {
  description = "Name of the Athena database"
  value       = "job_skills_db"  # Database managed manually
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.etl_trigger.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.etl_trigger.arn
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_dashboard" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "setup_complete" {
  description = "Confirmation message"
  value       = "✅ Job Skills Analyzer infrastructure deployed successfully!"
}
