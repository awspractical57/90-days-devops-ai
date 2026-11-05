# main.tf - resources to create
# terraform reads all .tf files in the folder together

terraform {
  # required_providers tells Terraform which plugin to download
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # minimum Terraform version required
  required_version = ">= 1.0"
}

# provider = which cloud and which region
provider "aws" {
  region = var.aws_region
}

# RESOURCE: S3 bucket
# format: resource "TYPE" "LOCAL_NAME"
# TYPE       = aws_s3_bucket (Terraform resource type)
# LOCAL_NAME = devops_bucket (name used inside .tf files only)
resource "aws_s3_bucket" "devops_bucket" {
  # bucket name must be globally unique across all AWS accounts
  bucket = var.bucket_name

  # tags apply to the resource in AWS
  tags = {
    Name        = var.bucket_name
    Environment = var.environment
    Project     = "90-days-devops-ai"
    Day         = "24"
  }
}

# RESOURCE: enable versioning on the bucket
# separate resource for versioning (Terraform AWS provider v4+)
resource "aws_s3_bucket_versioning" "devops_bucket_versioning" {
  # reference another resource: TYPE.LOCAL_NAME.ATTRIBUTE
  bucket = aws_s3_bucket.devops_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# RESOURCE: S3 bucket public access block
# best practice - block all public access by default
resource "aws_s3_bucket_public_access_block" "devops_bucket_pab" {
  bucket = aws_s3_bucket.devops_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
