# ============================================================================
# AWS COGNITO USER POOL (JWT Authentication)
# ============================================================================

resource "aws_cognito_user_pool" "api_users" {
  name = "job-skills-api-users"

  # Allow users to sign in with email
  username_attributes = ["email"]
  
  # Auto-verify email addresses
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Name    = "Job Skills API Users"
    Project = var.project_name
  }
}

# Cognito User Pool Client (for API access)
resource "aws_cognito_user_pool_client" "api_client" {
  name         = "job-skills-api-client"
  user_pool_id = aws_cognito_user_pool.api_users.id

  # Token validity
  access_token_validity  = 60  # 60 minutes
  id_token_validity      = 60  # 60 minutes
  refresh_token_validity = 30  # 30 days

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # OAuth flows
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  # Prevent secret (for public clients like web/mobile)
  generate_secret = false

  # Allowed OAuth flows
  allowed_oauth_flows = ["implicit", "code"]
  allowed_oauth_scopes = ["email", "openid", "profile"]
  
  # Callback URLs (for testing)
  callback_urls = ["http://localhost:8501"]
  logout_urls   = ["http://localhost:8501"]

  supported_identity_providers = ["COGNITO"]
}

# API Gateway Cognito Authorizer
resource "aws_api_gateway_authorizer" "cognito" {
  name            = "CognitoAuthorizer"
  rest_api_id     = aws_api_gateway_rest_api.job_skills_api.id
  type            = "COGNITO_USER_POOLS"
  provider_arns   = [aws_cognito_user_pool.api_users.arn]
  identity_source = "method.request.header.Authorization"
}
