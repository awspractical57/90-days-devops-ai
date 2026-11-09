# Day 25 - Terraform AWS Resources: VPC + EC2

## What I learned today

Day 24 was Terraform basics with one S3 bucket.
Day 25 is real infrastructure - VPC, subnet, IGW, route table, security group, key pair, EC2.
8 resources created with one apply. 8 resources deleted with one destroy.

---

## Concepts covered

### New Terraform concepts today

```
data source  = read existing AWS resource (not created by Terraform)
              used to fetch latest Amazon Linux 2023 AMI automatically
              never hardcode AMI IDs - they change per region and expire

locals       = computed values reused across resources
              like constants in code - define once, use everywhere
              cheaper than variables - no input needed

depends_on   = explicit dependency between resources
              EC2 depends_on IGW so nginx yum install has internet

user_data    = shell script that runs on EC2 first boot
              used to install nginx automatically
              <<-EOF ... EOF = heredoc syntax in HCL
```

### Data source syntax

```hcl
# data source - reads from AWS, creates nothing
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# reference it in a resource
ami = data.aws_ami.amazon_linux.id
```

### Locals syntax

```hcl
locals {
  project_tag = "90-days-devops-ai"
  name_prefix = "${var.environment}-devops"
}

# use with local. prefix
Name = "${local.name_prefix}-vpc"
```

### Resource creation order

Terraform figures out the order automatically from references:
```
VPC first (nothing depends on it)
IGW + subnet + SG + key pair in parallel (all depend on VPC only)
Route table (depends on VPC + IGW)
Route table association (depends on route table + subnet)
EC2 last (depends on subnet + SG + key pair + IGW via depends_on)
```

---

## Files written

### main.tf structure

```
provider "aws"                          - which region
locals                                  - name_prefix, project_tag
data "aws_ami"                          - fetch latest Amazon Linux 2023
aws_vpc                                 - 10.0.0.0/16
aws_subnet                              - 10.0.1.0/24 public
aws_internet_gateway                    - internet access
aws_route_table                         - 0.0.0.0/0 -> IGW
aws_route_table_association             - link subnet to route table
aws_security_group                      - SSH 22 + HTTP 80 inbound
aws_key_pair                            - SSH key from ~/.ssh/id_rsa.pub
aws_instance                            - t2.micro + nginx user_data
```

---

## Terminal output

```
terraform apply
  aws_key_pair created
  aws_vpc created: vpc-0cb5ae8ada36f283b
  aws_internet_gateway created: igw-013b69e971f6b2ddc
  aws_route_table created: rtb-034b5c9422cde8043
  aws_security_group created: sg-092346a906f134385
  aws_subnet created: subnet-0824dbadb57eae880
  aws_route_table_association created
  aws_instance created: i-07154250bf1892565
  Apply complete! Resources: 8 added, 0 changed, 0 destroyed.

Outputs:
  ami_used       = "ami-012d03f16a3f48db4"
  ec2_public_ip  = "65.0.204.189"
  ec2_public_dns = "ec2-65-0-204-189.ap-south-1.compute.amazonaws.com"
  ssh_command    = "ssh -i ~/.ssh/id_rsa ec2-user@65.0.204.189"
  vpc_id         = "vpc-0cb5ae8ada36f283b"

terraform destroy
  Destroy complete! Resources: 8 destroyed.
```

---

## Destroy order (automatic)

```
Terraform reversed the dependency graph automatically:
  route_table_association  (removed first - no dependencies)
  route_table              (after association removed)
  EC2 instance             (took 22s - AWS waits for clean shutdown)
  key_pair + SG + subnet + IGW in parallel
  VPC last                 (everything else must be gone first)
```

No manual cleanup needed. No DependencyViolation errors.
Compare this to Day 20 VPC cleanup with boto3 - manual order, multiple errors.

---

## Key rules

- Never hardcode AMI IDs - use data source, they change per region
- locals = define once, use everywhere with local. prefix
- depends_on = use when Terraform cannot infer dependency from references
- user_data runs once on first boot only - not on restart
- terraform output = read outputs after apply without re-applying
- Destroy order is automatic - Terraform reverses the dependency graph

---

## Terraform vs boto3 comparison

```
Day 20 VPC with boto3:
  - 150+ lines of Python
  - Manual cleanup order required
  - DependencyViolation errors when order was wrong
  - Had to run multiple CLI commands to debug

Day 25 VPC with Terraform:
  - 120 lines of HCL
  - Cleanup order automatic
  - Zero errors on destroy
  - terraform plan shows everything before it happens
```

---

## Files

```
Day-25/
├── main.tf              - VPC, subnet, IGW, RT, SG, key pair, EC2
├── variables.tf         - aws_region, environment, vpc_cidr, instance_type
├── outputs.tf           - vpc_id, ec2_public_ip, ssh_command, ami_used
├── terraform.tfvars     - variable values (not committed to git)
├── .gitignore           - excludes state files, tfvars, .terraform/
└── README.md            - this file
```

---

## Progress

| Day | Topic | Status |
|-----|-------|--------|
| 23 | Cost optimization | Done |
| 24 | Terraform basics | Done |
| 25 | Terraform VPC + EC2 | Done |
| 26 | Kubernetes basics | Next |

---

GitHub: [github.com/awspractical57/90-days-devops-ai](https://github.com/awspractical57/90-days-devops-ai)
