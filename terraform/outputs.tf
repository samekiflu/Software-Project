output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.users.id
}
output "cognito_client_id" {
  value = aws_cognito_user_pool_client.app.id
}
output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}
output "frontend_url" {
  value = aws_cloudfront_distribution.frontend.domain_name
}

