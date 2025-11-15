# ============================================================================
# JWT-AUTHENTICATED ENDPOINTS (v2)
# ============================================================================

# Create /auth resource (parent for JWT endpoints)
resource "aws_api_gateway_resource" "auth" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  parent_id   = aws_api_gateway_rest_api.job_skills_api.root_resource_id
  path_part   = "auth"
}

# Create /auth/{proxy+} for all JWT-protected routes
resource "aws_api_gateway_resource" "auth_proxy" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "{proxy+}"
}

# Method for /auth/{proxy+} with Cognito auth
resource "aws_api_gateway_method" "auth_proxy" {
  rest_api_id   = aws_api_gateway_rest_api.job_skills_api.id
  resource_id   = aws_api_gateway_resource.auth_proxy.id
  http_method   = "ANY"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# Integration with Lambda for JWT endpoints
resource "aws_api_gateway_integration" "auth_lambda" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  resource_id = aws_api_gateway_method.auth_proxy.resource_id
  http_method = aws_api_gateway_method.auth_proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api.invoke_arn
}

# Method for /auth root
resource "aws_api_gateway_method" "auth_root" {
  rest_api_id   = aws_api_gateway_rest_api.job_skills_api.id
  resource_id   = aws_api_gateway_resource.auth.id
  http_method   = "ANY"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# Integration with Lambda for /auth root
resource "aws_api_gateway_integration" "auth_lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id
  resource_id = aws_api_gateway_method.auth_root.resource_id
  http_method = aws_api_gateway_method.auth_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api.invoke_arn
}

# Update deployment to include new routes
resource "aws_api_gateway_deployment" "api_v2" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
    aws_api_gateway_integration.auth_lambda,
    aws_api_gateway_integration.auth_lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.job_skills_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.auth.id,
      aws_api_gateway_method.auth_proxy.id,
      aws_api_gateway_integration.auth_lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}
