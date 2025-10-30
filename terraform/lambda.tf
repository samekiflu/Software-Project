resource "aws_iam_role" "analyzer_lambda_role" {
  name = "resource-analyzer-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = { Service = "lambda.amazonaws.com" },
      Effect = "Allow"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.analyzer_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "analyzer" {
  function_name    = "resource-analyzer"
  role             = aws_iam_role.analyzer_lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  filename         = "../lambda/build/analyzer.zip"
  source_code_hash = filebase64sha256("../lambda/build/analyzer.zip")
  timeout          = 20
  memory_size      = 512

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.analysis_results.name
      GITHUB_TOKEN = var.github_token
      HF_API_TOKEN = var.hf_api_token
    }
  }

  tags = local.common_tags
}
