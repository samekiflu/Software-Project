resource "aws_apigatewayv2_api" "analysis_api" {
  name          = "analysis-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "analysis_integration" {
  api_id                 = aws_apigatewayv2_api.analysis_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.analyzer.arn
  payload_format_version = "2.0"
}

# Routes: /analyze/{type}
resource "aws_apigatewayv2_route" "analysis_route" {
  api_id    = aws_apigatewayv2_api.analysis_api.id
  route_key = "POST /analyze/{type}"
  target    = "integrations/${aws_apigatewayv2_integration.analysis_integration.id}"
}

resource "aws_lambda_permission" "api_invoke" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analyzer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.analysis_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.analysis_api.id
  name        = "dev"
  auto_deploy = true
}

output "analysis_api_url" {
  value = aws_apigatewayv2_stage.dev.invoke_url
}
