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

output "api_lambda_function_name" {
  description = "Name of the API Lambda function"
  value       = aws_lambda_function.api.function_name
}

output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = "${aws_api_gateway_stage.api.invoke_url}"
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.job_skills_api.id
}

output "api_usage_instructions" {
  description = "How to use the API"
  value = <<-EOT
  
  🚀 Your Job Skills Analyzer API is deployed!
  
  API Base URL: ${aws_api_gateway_stage.api.invoke_url}
  
  Test the API:
  
  1. Health Check:
     curl ${aws_api_gateway_stage.api.invoke_url}/health
  
  2. Get Stats (requires API key):
     curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
          ${aws_api_gateway_stage.api.invoke_url}/stats
  
  3. Get Top Skills:
     curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
          ${aws_api_gateway_stage.api.invoke_url}/skills/top?limit=10
  
  4. API Documentation:
     ${aws_api_gateway_stage.api.invoke_url}/docs
  
  EOT
}

# Cognito outputs
output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.api_users.id
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.api_users.arn
}

output "cognito_client_id" {
  description = "ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.api_client.id
}

output "cognito_instructions" {
  description = "How to create a test user and get JWT token"
  value = <<-EOT
  
  📝 Create a test user:
  
  aws cognito-idp sign-up \
    --client-id ${aws_cognito_user_pool_client.api_client.id} \
    --username test@example.com \
    --password TestPass123! \
    --user-attributes Name=email,Value=test@example.com
  
  🔐 Get JWT token:
  
  aws cognito-idp initiate-auth \
    --client-id ${aws_cognito_user_pool_client.api_client.id} \
    --auth-flow USER_PASSWORD_AUTH \
    --auth-parameters USERNAME=test@example.com,PASSWORD=TestPass123!
  
  EOT
}
