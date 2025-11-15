# ============================================================================
# API LAMBDA FUNCTION (FastAPI)
# ============================================================================

resource "aws_lambda_function" "api" {
  filename         = "${path.module}/../api/api-lambda.zip"
  function_name    = "JobSkillsAPI"
  role            = "arn:aws:iam::223280412524:role/LabRole"
  handler         = "lambda_handler.handler"
  source_code_hash = filebase64sha256("${path.module}/../api/api-lambda.zip")
  runtime         = "python3.13"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      API_KEY              = var.api_key
      DATABASE_NAME        = "job_skills_db"
      ATHENA_OUTPUT_BUCKET = aws_s3_bucket.athena_results.bucket
    }
  }

  tags = {
    Name    = "Job Skills API"
    Project = var.project_name
  }
}

# CloudWatch log group for API Lambda
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/lambda/JobSkillsAPI"
  retention_in_days = 7

  tags = {
    Name    = "Job Skills API Logs"
    Project = var.project_name
  }
}

# ============================================================================
# API GATEWAY REST API
# ============================================================================

resource "aws_api_gateway_rest_api" "job_skills_api" {
  name        = "JobSkillsAnalyzerAPI"
  description = "Job Skills Analyzer API - Real-time job market intelligence"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name    = "Job Skills API Gateway"
    Project = var.project_name
  }
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  parent_id   = aws_api_gateway_rest_api.job_skills_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.job_skills_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api.invoke_arn
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.job_skills_api.id
  resource_id   = aws_api_gateway_rest_api.job_skills_api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api.invoke_arn
}

# resource "aws_api_gateway_deployment" "api" {
#   depends_on = [
#     aws_api_gateway_integration.lambda,
#     aws_api_gateway_integration.lambda_root,
#   ]
# 
#   rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
# 
#   lifecycle {
#     create_before_destroy = true
#   }
# }

resource "aws_api_gateway_stage" "api" {
  deployment_id = aws_api_gateway_deployment.api_v2.id
  rest_api_id   = aws_api_gateway_rest_api.job_skills_api.id
  stage_name    = var.environment


  tags = {
    Name    = "Job Skills API Stage"
    Project = var.project_name
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/job-skills-api"
  retention_in_days = 7

  tags = {
    Name    = "Job Skills API Gateway Logs"
    Project = var.project_name
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.job_skills_api.execution_arn}/*/*"
}

resource "aws_api_gateway_usage_plan" "api_plan" {
  name        = "job-skills-api-plan"
  description = "Usage plan for Job Skills API with rate limiting"

  api_stages {
    api_id = aws_api_gateway_rest_api.job_skills_api.id
    stage  = aws_api_gateway_stage.api.stage_name
  }

  quota_settings {
    limit  = 10000
    period = "DAY"
  }

  throttle_settings {
    burst_limit = 200
    rate_limit  = 100
  }
}

resource "aws_cloudwatch_metric_alarm" "api_errors" {
  alarm_name          = "JobSkillsAPIHighErrorRate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Alert when API Lambda has more than 5 errors in 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "api_latency" {
  alarm_name          = "JobSkillsAPIHighLatency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Average"
  threshold           = 5000
  alarm_description   = "Alert when API response time exceeds 5 seconds"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }
}
