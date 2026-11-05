# Day 24 - Terraform Basics: Infrastructure as Code

## What I learned today

Terraform = define AWS infrastructure as code in .tf files.
Instead of clicking in console or running CLI commands manually,
you write what you want and Terraform figures out how to create it.

The key shift in thinking:
- AWS CLI = imperative: you say exactly HOW (create this, then that)
- Terraform = declarative: you say WHAT you want, it figures out HOW

---

## Concepts covered

### Core workflow

```
terraform init     = download provider plugins (like npm install)
terraform plan     = show what WILL change, nothing created yet (dry run)
terraform apply    = create/update resources (type yes to confirm)
terraform destroy  = delete everything Terraform manages (type yes to confirm)
```

### Core files

```
main.tf            = resources to create
variables.tf       = input variables (like function parameters)
outputs.tf         = values to display after apply (like return values)
terraform.tfvars   = variable values (like .env - never commit to git)
.terraform/        = downloaded provider plugins (like node_modules)
terraform.tfstate  = state file - never delete, never edit manually
```

### State file

```
terraform.tfstate = JSON file tracking everything Terraform created
Terraform uses it to know:
  - what resources already exist
  - what changed between plan runs
  - what to delete on terraform destroy

Never delete it. Never edit it manually.
If lost, Terraform has no memory of what it created.
```

### Resource reference syntax

```hcl
# format: resource "TYPE" "LOCAL_NAME"
resource "aws_s3_bucket" "devops_bucket" {
  bucket = var.bucket_name
}

# reference another resource: TYPE.LOCAL_NAME.ATTRIBUTE
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.devops_bucket.id
}
```

### Variables

```hcl
# variables.tf - define the variable
variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}

# terraform.tfvars - set the value
bucket_name = "my-unique-bucket-name"

# main.tf - use the variable
bucket = var.bucket_name
```

---

## Files written

### main.tf

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "devops_bucket" {
  bucket = var.bucket_name
  tags = {
    Name        = var.bucket_name
    Environment = var.environment
    Project     = "90-days-devops-ai"
    Day         = "24"
  }
}

resource "aws_s3_bucket_versioning" "devops_bucket_versioning" {
  bucket = aws_s3_bucket.devops_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "devops_bucket_pab" {
  bucket                  = aws_s3_bucket.devops_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### variables.tf

```hcl
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "bucket_name" {
  description = "S3 bucket name - must be globally unique"
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  default     = "dev"
}
```

### outputs.tf

```hcl
output "bucket_name" {
  description = "Name of the S3 bucket created"
  value       = aws_s3_bucket.devops_bucket.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.devops_bucket.arn
}

output "bucket_region" {
  description = "Region where bucket was created"
  value       = aws_s3_bucket.devops_bucket.region
}
```

---

## Terminal output

```
terraform init
  Installing hashicorp/aws v5.100.0
  Terraform has been successfully initialized!

terraform plan
  + aws_s3_bucket.devops_bucket
  + aws_s3_bucket_public_access_block.devops_bucket_pab
  + aws_s3_bucket_versioning.devops_bucket_versioning
  Plan: 3 to add, 0 to change, 0 to destroy.

terraform apply
  aws_s3_bucket.devops_bucket: Creating...
  aws_s3_bucket.devops_bucket: Creation complete after 2s
  aws_s3_bucket_public_access_block: Creation complete after 0s
  aws_s3_bucket_versioning: Creation complete after 1s
  Apply complete! Resources: 3 added, 0 changed, 0 destroyed.

  Outputs:
  bucket_arn    = "arn:aws:s3:::devops-journey-harsha-tf-day24"
  bucket_name   = "devops-journey-harsha-tf-day24"
  bucket_region = "ap-southeast-1"

terraform state list
  aws_s3_bucket.devops_bucket
  aws_s3_bucket_public_access_block.devops_bucket_pab
  aws_s3_bucket_versioning.devops_bucket_versioning

terraform destroy
  Destroy complete! Resources: 3 destroyed.
```

---

## Key rules

- `terraform plan` before every `apply` - always review what will change
- Never commit `terraform.tfvars` to git - it contains sensitive values
- Never commit `terraform.tfstate` to git - it contains resource IDs and may contain secrets
- Never delete `terraform.tfstate` - Terraform loses track of what it created
- `~> 5.0` in version means 5.x only - allows patch updates, blocks major version changes
- S3 versioning is a separate resource in AWS provider v4+ - not inside `aws_s3_bucket`
- `terraform destroy` deletes everything - only run when you mean it

---

## Terraform vs AWS CLI vs boto3

```
AWS CLI  = one command at a time, no state tracking, manual cleanup
boto3    = Python scripts, flexible, you manage state yourself
Terraform = declarative, tracks state, plan before apply, one destroy cleans all

Use Terraform when:
- Creating multiple related resources together
- Need to recreate same infrastructure in multiple environments
- Team needs to review infrastructure changes (terraform plan in PR)
- Need audit trail of what was created and when
```

---

## .gitignore for Terraform

```
terraform.tfstate
terraform.tfstate.backup
.terraform/
.terraform.lock.hcl
terraform.tfvars
*.tfplan
crash.log
```

---

## Files

```
Day-24/
├── main.tf              - S3 bucket + versioning + public access block
├── variables.tf         - aws_region, bucket_name, environment
├── outputs.tf           - bucket_name, bucket_arn, bucket_region
├── terraform.tfvars     - variable values (not committed to git)
├── .gitignore           - excludes state files and tfvars
└── README.md            - this file
```

---

## Progress

| Day | Topic | Status |
|-----|-------|--------|
| 21 | Lambda serverless | Done |
| 22 | CloudWatch monitoring | Done |
| 23 | Cost optimization | Done |
| 24 | Terraform basics | Done |
| 25 | Terraform AWS resources | Next |

---

GitHub: [github.com/awspractical57/90-days-devops-ai](https://github.com/awspractical57/90-days-devops-ai)