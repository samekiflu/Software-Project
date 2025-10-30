terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"   # or your team’s region
}

locals {
  common_tags = {
    Project = "SoftwareProject"
    Env     = "dev"
    Owner   = "Team"
  }
}

