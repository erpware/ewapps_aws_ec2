provider "aws" {
  region  = "eu-central-1"
  profile = "erpware"
  default_tags {
    tags = {
      "ew:terraform" = "yes"
    }
  }
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  required_version = ">= 0.13"
}
