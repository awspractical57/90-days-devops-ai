variable "aws_region" {
    description = "AWS region"
    type        = string
    default     = "ap-south-1"
}

variable "environment" {
    description = "Environment name"
    type        = string
    default     = "dev"
}

variable "vpc_cidr"{
    description = "VPC CIDR block"
    type        = string
    default     = "10.0.0.0/16"
}

variable "public_subnet_cidr"{
    description = "Public Subnet CIDR block"
    type        = string
    default     = "10.0.1.0/24"
}

variable "instance_type"{
    description = "EC2 instance type"
    type        = string
    default     = "t2.micro"
}

variable "public_key_path"{
    description = "Path to SSH public key file"
    type        = string
    default     = "~/.ssh/id_rsa.pub"
}