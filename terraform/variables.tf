variable "aws_region" { default = "us-east-1" }
variable "project"    { default = "software-project" }
variable "env"        { default = "dev" }

variable "github_token" {
  description = "GitHub Personal Access Token"
  type        = string
  default     = ""
}

variable "hf_api_token" {
  description = "Hugging Face Token"
  type        = string
  default     = ""
}
