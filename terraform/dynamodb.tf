resource "aws_dynamodb_table" "analysis_results" {
  name         = "resource_analysis_results"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = local.common_tags
}
