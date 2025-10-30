terraform {
  backend "s3" {
    bucket         = "software-project-terraform-state"   # create this bucket in AWS first
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "software-project-tf-locks"          # create this table in AWS first
    encrypt        = true
  }
}

