terraform{
    required_providers{
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
    required_version = ">= 1.0"
}

provider "aws"{
    region = var.aws_region
}

# LOCALS - computed values reused across resources
# cheaper then variables - no input needed, just calculations
locals{
    project_tag = "90-days-devops-ai"
    name_prefix = "${var.environment}-devops"
}
# DATA SOURCE - read existing aws resources (not created by us)
# get the latest Amazon Linux 2023 AMI automatically
# so we never hardcode the AMI ID that gets outdated
data "aws_ami""amazon_linux"{
    most_recent = true
    owners = ["amazon"]
    filter{
        name = "name"
        values = ["al2023-ami-*-x86_64"]
    }
    filter{
        name = "state"
        values = ["available"]
    }
}

# VPC
resource "aws_vpc" "main"{
    cidr_block = var.vpc_cidr
    enable_dns_support = true
    enable_dns_hostnames = true

    tags ={
        Name = "${local.name_prefix}-vpc"
        Environment = var.environment
        Project = local.project_tag
    }
}

# PUBLIC SUBNET
resource "aws_subnet" "public"{
    vpc_id = aws_vpc.main.id
    cidr_block = var.public_subnet_cidr
    availability_zone = "${var.aws_region}a"
    map_public_ip_on_launch = true
    tags ={
        Name = "${local.name_prefix}-public-subnet"
        Environment = var.environment
        Project = local.project_tag
    }
}

# INTERNET GATEWAY
resource "aws_internet_gateway" "main"{
    vpc_id = aws_vpc.main.id
    tags ={
        Name = "${local.name_prefix}-igw"
        Environment = var.environment
        Project = local.project_tag
    }
}

# ROUTE TABLE
resource "aws_route_table" "public"{
    vpc_id = aws_vpc.main.id
    #route all internet traffic through IGW
    route{
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.main.id
    }
    tags ={
        Name = "${local.name_prefix}-public-rt"
        Environment = var.environment
        Project = local.project_tag
    }
}

# ROUTE TABLE ASSOCIATION - links subnet to route table
resource "aws_route_table_association" "public"{
    subnet_id = aws_subnet.public.id
    route_table_id = aws_route_table.public.id
}

# SECURITY GROUP - firewall rules for EC2
resource "aws_security_group" "ec2_sg"{
    name = "${local.name_prefix}-ec2-sg"
    description = "Security group for DevOps Journey EC2"
    vpc_id = aws_vpc.main.id

    # inbound: allow SSH from anywhere (learning only - restrict in production)
    ingress{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        description = "SSH access"
    }

    # inbound: allow HTTP
    ingress{
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        description = "HTTP access"
    }

    # outbound: allow all traffic out
    egress{
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow all outbound traffic"
    }

    tags = {
        Name = "${local.name_prefix}-ec2-sg"
        Environment = var.environment
        Project = local.project_tag
    }
}

# KEY PAIR - for SSH access to EC2
# generates key pair from public key file
resource "aws_key_pair" "devops_key"{
    key_name = "${local.name_prefix}-key"
    public_key = file(var.public_key_path)

    tags = {
        Name = "${local.name_prefix}-key"
        Environment = var.environment
        Project = local.project_tag
    }
}

# EC2 INSTANCE
resource "aws_instance" "devops_ec2"{
    # use AMI from data source - always latest Amazon Linux 2023
    ami = data.aws_ami.amazon_linux.id
    instance_type = var.instance_type

    # place in public subnet so we can SSH in
    subnet_id = aws_subnet.public.id
    vpc_security_group_ids = [aws_security_group.ec2_sg.id]
    key_name = aws_key_pair.devops_key.key_name

    # user_data runs on first boot
    # install nginx automatically when instance starts
    user_data = <<-EOF
                #!/bin/bash
                yum update -y
                yum install -y nginx
                systemctl start nginx
                systemctl enable nginx
                echo "<h1>Day 25 - Terraform EC2</h1>" > /usr/share/nginx/html/index.html
                EOF

                tags = {
                    Name = "${local.name_prefix}-ec2"
                    Environment = var.environment
                    Project = local.project_tag
                    Day = "25"
                }

                # explicit dependency - EC2 needs IGW to each internet for yum
                depends_on = [aws_internet_gateway.main]    
}