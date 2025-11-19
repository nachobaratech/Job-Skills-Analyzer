# ============================================================================
# Job Market Skills Gap Analyzer - Terraform Infrastructure
# ============================================================================

# ============================================================================
# S3 BUCKETS
# ============================================================================

# Raw data bucket
resource "aws_s3_bucket" "raw" {
  bucket = "job-skills-raw-${var.account_id}"

  tags = {
    Name        = "Job Skills Raw Data"
    Project     = var.project_name
    Environment = "production"
  }
}


# Athena results bucket
resource "aws_s3_bucket" "athena_results" {
  bucket = "job-skills-athena-results-${var.account_id}"

  tags = {
    Name        = "Job Skills Athena Results"
    Project     = var.project_name
    Environment = "production"
  }
}

# Block public access for all buckets
resource "aws_s3_bucket_public_access_block" "raw" {
  bucket = aws_s3_bucket.raw.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================================================
# ATHENA DATABASE & TABLE
# ============================================================================

# Athena database exists - managed manually
# resource "aws_athena_database" "job_skills_db" {
#   name   = "job_skills_db"
#   bucket = aws_s3_bucket.athena_results.id
# 
# }

# Note: Athena tables with complex structures are better created via SQL
# We'll create a null_resource to run the CREATE TABLE statement
resource "null_resource" "athena_table" {
  # depends_on = [aws_athena_database.job_skills_db] # Database managed manually

  provisioner "local-exec" {
    command = <<-EOT
      aws athena start-query-execution \
        --query-string "CREATE EXTERNAL TABLE IF NOT EXISTS job_skills_db.jobs_with_skills (id STRING, title STRING, company STRING, description STRING, skills ARRAY<STRING>, skill_count INT) PARTITIONED BY (dt STRING) STORED AS PARQUET LOCATION 's3://${aws_s3_bucket.raw.bucket}/processed/'" \
        --result-configuration OutputLocation=s3://${aws_s3_bucket.athena_results.bucket}/ \
        --region ${var.aws_region}
    EOT
  }
}

# ============================================================================
# IAM ROLES & POLICIES
# ============================================================================

# Lambda execution role
# resource "aws_iam_role" "lambda_role" {
#   name = "JobSkillsLambdaRole"
# 
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = {
#         Service = "lambda.amazonaws.com"
#       }
#     }]
#   })
# 
#   tags = {
#     Name    = "Job Skills Lambda Role"
#     Project = var.project_name
#   }
# }

# Lambda policy for CloudWatch Logs
# resource "aws_iam_role_policy_attachment" "lambda_logs" {
#   role       = aws_iam_role.lambda_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# }

# Lambda policy for S3 access
# resource "aws_iam_role_policy" "lambda_s3" {
#   name = "JobSkillsLambdaS3Policy"
#   role = aws_iam_role.lambda_role.id
# 
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "s3:GetObject",
#           "s3:ListBucket"
#         ]
#         Resource = [
#           aws_s3_bucket.raw.arn,
#           "${aws_s3_bucket.raw.arn}/*"
#         ]
#       }
#     ]
#   })
# }

# Lambda policy for Athena access
# resource "aws_iam_role_policy" "lambda_athena" {
#   name = "JobSkillsLambdaAthenaPolicy"
#   role = aws_iam_role.lambda_role.id
# 
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "athena:StartQueryExecution",
#           "athena:GetQueryExecution",
#           "athena:GetQueryResults",
#           "glue:GetTable",
#           "glue:GetPartitions"
#         ]
#         Resource = "*"
#       },
#       {
#         Effect = "Allow"
#         Action = [
#           "s3:PutObject",
#           "s3:GetObject"
#         ]
#         Resource = "${aws_s3_bucket.athena_results.arn}/*"
#       }
#     ]
#   })
# }

# Lambda policy for SNS access
# resource "aws_iam_role_policy" "lambda_sns" {
#   name = "JobSkillsLambdaSNSPolicy"
#   role = aws_iam_role.lambda_role.id
# 
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "sns:Publish"
#         ]
#         Resource = aws_sns_topic.alerts.arn
#       }
#     ]
#   })
# }

# ============================================================================
# LAMBDA FUNCTION
# ============================================================================

# Create Lambda deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/etl_trigger.py"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "etl_trigger" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "JobSkillsETLTrigger"
  role            = "arn:aws:iam::223280412524:role/LabRole"
  handler         = "etl_trigger.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
      ATHENA_DATABASE = "job_skills_db"  # Database managed manually
      ATHENA_OUTPUT_LOCATION = "s3://${aws_s3_bucket.athena_results.bucket}/"
    }
  }

  tags = {
    Name    = "Job Skills ETL Trigger"
    Project = var.project_name
  }
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.etl_trigger.function_name}"
  retention_in_days = 7

  tags = {
    Name    = "Job Skills Lambda Logs"
    Project = var.project_name
  }
}

# ============================================================================
# S3 BUCKET NOTIFICATIONS → LAMBDA
# ============================================================================

# Allow S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.etl_trigger.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw.arn
}

# S3 bucket notification configuration
resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = aws_s3_bucket.raw.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.etl_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "processed/"
    filter_suffix       = ".jsonl"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

# ============================================================================
# SNS TOPIC FOR NOTIFICATIONS
# ============================================================================

resource "aws_sns_topic" "alerts" {
  name = "job-skills-alerts"

  tags = {
    Name    = "Job Skills Alerts"
    Project = var.project_name
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.email_address
}

# ============================================================================
# CLOUDWATCH DASHBOARD
# ============================================================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "JobSkillsAnalyzer"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/S3", "BucketSizeBytes", { stat = "Average", period = 86400 }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "S3 Bucket Size"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum" }],
            [".", "Errors", { stat = "Sum" }],
            [".", "Duration", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Lambda Metrics"
        }
      }
    ]
  })
}

# ============================================================================
# CLOUDWATCH ALARM
# ============================================================================

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "JobSkillsHighErrorRate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 2
  alarm_description   = "Alert when Lambda function has more than 2 errors in 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.etl_trigger.function_name
  }

  tags = {
    Name    = "Job Skills Lambda Error Alarm"
    Project = var.project_name
  }
}

# ============================================================================
# EVENTBRIDGE RULE FOR SCHEDULING
# ============================================================================

resource "aws_cloudwatch_event_rule" "daily_check" {
  name                = "JobSkillsDailyCheck"
  description         = "Trigger daily check at 9 AM UTC"
  schedule_expression = "cron(0 9 * * ? *)"

  tags = {
    Name    = "Job Skills Daily Check"
    Project = var.project_name
  }
}

# Note: Target would be added here if we had a function to trigger
# For now, the rule exists but isn't connected to anything


# EventBridge target - trigger ETL Lambda daily
resource "aws_cloudwatch_event_target" "trigger_etl_daily" {
  rule      = aws_cloudwatch_event_rule.daily_check.name
  target_id = "TriggerETLLambda"
  arn       = aws_lambda_function.etl_trigger.arn
}

# Allow EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.etl_trigger.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_check.arn
}
