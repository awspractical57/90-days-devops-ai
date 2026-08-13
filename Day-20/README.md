# Day 20 - AWS VPC Deep Dive

## What is today about?

VPC controls how your AWS resources connect to each other and to the internet. Today we build a complete VPC from scratch with public and private subnets, internet gateway, route tables, and security groups - all automated with Python boto3.

---

## How real companies use VPC

| Concept | Real company use case |
|---------|----------------------|
| Public subnet | Load balancers and web servers that need internet access |
| Private subnet | Databases and internal services - never directly exposed |
| Security groups | Restrict database access to only application servers |
| Multiple VPCs | Separate dev, staging, production environments completely |

---

## Core Concepts

```
VPC = Virtual Private Cloud
Your own private network inside AWS

Subnet = a sub-section of the VPC's IP address range
Public subnet  = has a route to an Internet Gateway
Private subnet = no route to internet, fully isolated

Internet Gateway (IGW) = connects VPC to the internet
Route Table = rules deciding where network traffic goes
Security Group = firewall at instance level (stateful)
NACL = firewall at subnet level (stateless)
```

**Office building analogy:**
```
VPC            = the building
Subnets        = floors
Public subnet  = ground floor, public can enter
Private subnet = upper floors, restricted access
Route table    = building directory
Security Group = ID card reader, remembers you for return trip
NACL           = security guard, checks you every single time
```

---

## CIDR Blocks Explained

```
CIDR = Classless Inter-Domain Routing
A way to define a range of IP addresses

10.0.0.0/16 means:
First 16 bits are fixed (10.0)
Remaining 16 bits are usable
Total addresses = 65,536 (10.0.0.0 to 10.0.255.255)

10.0.1.0/24 means:
First 24 bits are fixed (10.0.1)
Remaining 8 bits are usable
Total addresses = 256 (10.0.1.0 to 10.0.1.255)

Smaller number after slash = more addresses
/16 = 65536 addresses
/24 = 256 addresses
/32 = 1 address (a single host)
```

---

## Public vs Private Subnet - The Real Difference

```
Both subnets can have identical CIDR ranges.
The ONLY difference is the route table.

Public subnet route table:
0.0.0.0/0 -> Internet Gateway
(all traffic not in the VPC goes to the internet)

Private subnet route table:
10.0.0.0/16 -> local
(no route to internet gateway - traffic outside VPC has nowhere to go)

This is why a subnet becomes "public" or "private"
based on ONE routing rule, not anything inherent to the subnet itself.
```

---

## Security Group vs NACL

```
Security Group (instance level):
Stateful - if inbound is allowed, outbound response is automatic
Default: deny all inbound, allow all outbound
Applied to: EC2 instances, RDS, Lambda etc

NACL (subnet level):
Stateless - inbound and outbound rules are separate, both needed
Default: allow all traffic
Applied to: entire subnet, affects every instance inside it

Most setups only need Security Groups.
NACLs are for extra defense-in-depth in regulated environments.
```

---

## AWS CLI Commands Practiced

```bash
# list default VPC
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock,IsDefault]' --output table

# create custom VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=devops-journey-vpc}]'

# list subnets in a VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-xxxxx" --output table

# create a subnet
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.1.0/24 \
  --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet}]'

# create internet gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=devops-igw}]'

# attach internet gateway to VPC
aws ec2 attach-internet-gateway --internet-gateway-id igw-xxxxx --vpc-id vpc-xxxxx
```

---

## Script - vpc_builder.py

**What it does:**
```
Creates a custom VPC with 10.0.0.0/16 CIDR
Creates a public subnet (auto-assigns public IPs)
Creates a private subnet (fully isolated)
Creates and attaches an Internet Gateway
Creates a route table and associates it with the public subnet
Creates a security group allowing SSH and HTTP
Generates a JSON report of the entire architecture
Cleans up everything in the correct order
```

**Key functions explained:**

```python
# create VPC - waits until fully available before continuing
ec2.create_vpc(CidrBlock='10.0.0.0/16')
waiter = ec2.get_waiter('vpc_available')
waiter.wait(VpcIds=[vpc_id])

# create subnet - public subnets need MapPublicIpOnLaunch
ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.1.0/24', AvailabilityZone='ap-south-1a')
ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': True})

# internet gateway must be created then attached separately
ec2.create_internet_gateway()
ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

# route table - the rule that makes a subnet "public"
ec2.create_route(RouteTableId=rt_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)

# security group with inbound rules
ec2.create_security_group(GroupName=name, VpcId=vpc_id)
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[{'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}]
)
```

**Cleanup order matters:**
```
1. Security group (no dependents)
2. Subnets (must be empty - no instances inside)
3. Detach then delete Internet Gateway
4. Delete VPC last (must have nothing left inside it)

Deleting in wrong order causes DependencyViolation errors.
```

**How to run:**
```bash
python3 vpc_builder.py
```

---

## Key Lessons from Day 20

> Lesson 1: A subnet is public or private based entirely on its route table, not anything inherent to the subnet. Add a route to an Internet Gateway, it becomes public.

> Lesson 2: Internet Gateways must be created AND attached separately. Creating one without attaching it does nothing.

> Lesson 3: Security Groups are stateful, NACLs are stateless. This is one of the most commonly asked interview questions in networking.

> Lesson 4: Always clean up VPC resources in reverse dependency order - security group, subnets, detach and delete IGW, then VPC last.

> Lesson 5: Never expose SSH (port 22) to 0.0.0.0/0 in production. Restrict to specific IP ranges or use a bastion host / Session Manager.

---

## Interview Questions

1. **What is the difference between a public and private subnet?**
   > A public subnet has a route table entry sending internet-bound traffic (0.0.0.0/0) to an Internet Gateway. A private subnet has no such route, so it cannot reach or be reached from the internet directly. The subnet's CIDR range itself has nothing to do with this - it's purely the routing configuration.

2. **What is the difference between a Security Group and a Network ACL?**
   > Security Groups operate at the instance level and are stateful - if you allow inbound traffic, the response traffic is automatically allowed outbound. NACLs operate at the subnet level and are stateless - you must explicitly allow both inbound and outbound traffic separately. Security Groups only support allow rules, NACLs support both allow and deny.

3. **What is a CIDR block and how do you calculate available IPs?**
   > CIDR notation defines an IP range using a base address and a prefix length. The prefix length tells you how many bits are fixed. A /16 has 16 fixed bits and 16 variable bits, giving 2^16 = 65,536 addresses. A /24 has 24 fixed bits and 8 variable bits, giving 2^8 = 256 addresses.

4. **What is the purpose of a NAT Gateway?**
   > A NAT Gateway lets instances in a private subnet initiate outbound connections to the internet (like downloading updates) while preventing inbound connections from the internet to those instances. It sits in a public subnet and routes private subnet traffic through it.

5. **How would you design a secure VPC architecture for a web application?**
   > Public subnet for load balancers only. Private subnet for application servers, with a NAT Gateway for outbound updates. A separate private subnet (often called data subnet) for databases with even stricter security groups, only allowing traffic from the application subnet.

---

## Troubleshooting

| Error | Why | Fix |
|-------|-----|-----|
| DependencyViolation on delete | Resources still attached | Delete in reverse order: SG, subnet, IGW, VPC |
| InvalidSubnet.Range | CIDR not inside VPC range | Subnet CIDR must be within the VPC's CIDR block |
| Instance has no internet access | Missing route or IGW not attached | Check route table has 0.0.0.0/0 to IGW |
| Cannot SSH to instance | Security group blocks port 22 | Add inbound rule for port 22 from your IP |
| CIDR block already in use | Overlapping subnet ranges | Use non-overlapping CIDR blocks like 10.0.1.0/24 and 10.0.2.0/24 |

---

## Files in This Folder

```
Day-20/
  README.md          - this file
  .env               - config, not in GitHub
  .gitignore         - excludes .env and reports
  vpc_builder.py     - full VPC automation script
```

---

## Previous Day
[Day 19 - AWS IAM Deep Dive](../Day-19/)

## Next Day
[Day 21 - AWS Lambda Serverless Automation](../Day-21/)

---

Part of my [90-Day DevOps + AI Journey](../../README.md) - documented daily for beginners and professionals alike.
