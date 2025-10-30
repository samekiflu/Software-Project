########################################
# SNS topic for alarm notifications
########################################
resource "aws_sns_topic" "alerts" {
  name = "software-project-alerts"
  tags = local.common_tags
}

########################################
# CloudWatch log group retention policy
########################################
resource "aws_cloudwatch_log_group" "default" {
  name              = "/aws/lambda/default_retention"
  retention_in_days = 30
  tags              = local.common_tags
}

########################################
# Cognito User Pool & App Client
########################################
resource "aws_cognito_user_pool" "users" {
  name = "software-users"
  auto_verified_attributes = ["email"]
  tags = local.common_tags
}

resource "aws_cognito_user_pool_client" "app" {
  name            = "web-client"
  user_pool_id    = aws_cognito_user_pool.users.id
  generate_secret = false
  callback_urls   = ["http://localhost:5173"]
  logout_urls     = ["http://localhost:5173"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows  = ["code"]
  allowed_oauth_scopes = ["openid", "email"]
  tags = local.common_tags
}

resource "aws_cognito_user_group" "admin" {
  name         = "Admin"
  user_pool_id = aws_cognito_user_pool.users.id
  description  = "Administrators"
}
resource "aws_cognito_user_group" "member" {
  name         = "Member"
  user_pool_id = aws_cognito_user_pool.users.id
  description  = "Standard users"
}

########################################
# CloudWatch Dashboard (Observability)
########################################
resource "aws_cloudwatch_dashboard" "health" {
  dashboard_name = "ServiceHealth"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric",
        properties = {
          metrics = [["AWS/Lambda","Errors","FunctionName","example-lambda"]],
          region  = "us-east-1",
          title   = "Lambda Errors (example)"
        }
      }
    ]
  })
}

########################################
# CloudFront + S3 (frontend hosting)
########################################
resource "aws_s3_bucket" "frontend" {
  bucket = "software-project-frontend"
  website {
    index_document = "index.html"
    error_document = "index.html"
  }
  tags = local.common_tags
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled = true

  origins {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "s3-origin"
  }

  default_cache_behavior {
    target_origin_id = "s3-origin"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods = ["GET","HEAD"]
    cached_methods  = ["GET","HEAD"]
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions { geo_restriction { restriction_type = "none" } }

  default_root_object = "index.html"
  tags = local.common_tags
}

