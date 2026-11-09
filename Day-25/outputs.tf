output "vpc_id" {
    description = "VPC_ID"
    value = aws_vpc.main.id
}

output "ec2_public_ip"{
    description = "EC2 public IP address"
    value = aws_instance.devops_ec2.public_ip
}
output "ec2_public_dns"{
    description = "EC2 public DNS"
    value = aws_instance.devops_ec2.public_dns
}
output "ami_used"{
    description = "AMI used for EC2 instance"
    value = data.aws_ami.amazon_linux.id
}
output "ssh_command"{
    description = "Command to SSH into EC2"
    value = "ssh -i ~/.ssh/id_rsa ec2-user@${aws_instance.devops_ec2.public_ip}"
}