# IAM Role - Using AWS Academy LabRole
# Custom IAM role creation commented out for AWS Academy environment
# Lambda function configured to use existing LabRole

# Uncomment below for non-Academy AWS accounts:
/*
resource "aws_iam_role" "lambda_role" {
  name = "JobSkillsLambdaRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
  tags = {
    Name    = "Job Skills Lambda Role"
    Project = var.project_name
  }
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "JobSkillsLambdaS3Policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.raw.arn,
        "${aws_s3_bucket.raw.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy" "lambda_athena" {
  name = "JobSkillsLambdaAthenaPolicy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "glue:GetTable",
          "glue:GetPartitions"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject"]
        Resource = "${aws_s3_bucket.athena_results.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_sns" {
  name = "JobSkillsLambdaSNSPolicy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["sns:Publish"]
      Resource = aws_sns_topic.alerts.arn
    }]
  })
}
*/

