# variables.tf = input variables
# like function parameters - make code reusable

variable "aws_region"{
    description = "The AWS region to deploy resources"
    type        = string
    # default value used if no value is provided in tfvars
    default     = "ap-southeast-1"
}

variable "bucket_name"{
    description = "s3 bucket name - must be globally unique"
    type        = string
    # no default value - must be provided in tfvars
}

variable "environment"{
    description = "environment name - dev, test, prod"
    type        = string
    default     = "dev"
}
