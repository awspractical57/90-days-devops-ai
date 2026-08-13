import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
VPC_CIDR = os.getenv('VPC_CIDR', '10.0.0.0/16')
PUBLIC_CIDR = os.getenv('PUBLIC_SUBNET_CIDR', '10.0.1.0/24')
PRIVATE_CIDR = os.getenv('PRIVATE_SUBNET_CIDR', '10.0.2.0/24')


def get_ec2_client():
    # VPC operations use the EC2 client since VPC is part of EC2 service
    return boto3.client('ec2', region_name=REGION)


def create_vpc(name):
    # CIDR block defines IP range
    # 10.0.0.0/16 means 65536 addresses, from 10.0.0.0 to 10.0.255.255
    ec2 = get_ec2_client()
    response = ec2.create_vpc(
        CidrBlock=VPC_CIDR,
        TagSpecifications=[
            {'ResourceType': 'vpc', 'Tags': [{'Key': 'Name', 'Value': name}]}
        ]
    )
    vpc_id = response['Vpc']['VpcId']
    print(f"VPC created: {vpc_id} ({VPC_CIDR})")

    # wait until VPC is fully available before next steps
    waiter = ec2.get_waiter('vpc_available')
    waiter.wait(VpcIds=[vpc_id])

    return vpc_id


def create_subnet(vpc_id, cidr, az, name, public=False):
    # az = availability zone, a physical data center location
    # subnet CIDR must be smaller and inside the VPC CIDR range
    ec2 = get_ec2_client()
    response = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cidr,
        AvailabilityZone=az,
        TagSpecifications=[
            {'ResourceType': 'subnet', 'Tags': [{'Key': 'Name', 'Value': name}]}
        ]
    )
    subnet_id = response['Subnet']['SubnetId']

    # public subnets auto-assign public IP to any instance launched in them
    if public:
        ec2.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )

    subnet_type = "PUBLIC" if public else "PRIVATE"
    print(f"{subnet_type} subnet created: {subnet_id} ({cidr})")
    return subnet_id


def create_internet_gateway(vpc_id, name):
    # IGW is the door connecting VPC to internet
    # must be created then attached separately
    ec2 = get_ec2_client()
    response = ec2.create_internet_gateway(
        TagSpecifications=[
            {'ResourceType': 'internet-gateway', 'Tags': [{'Key': 'Name', 'Value': name}]}
        ]
    )
    igw_id = response['InternetGateway']['InternetGatewayId']

    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Internet Gateway created and attached: {igw_id}")
    return igw_id


def create_route_table(vpc_id, igw_id, subnet_id, name):
    # route table decides where traffic goes
    # 0.0.0.0/0 means all internet traffic
    # without this route, subnet has no internet access even with IGW attached
    ec2 = get_ec2_client()
    response = ec2.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {'ResourceType': 'route-table', 'Tags': [{'Key': 'Name', 'Value': name}]}
        ]
    )
    rt_id = response['RouteTable']['RouteTableId']

    ec2.create_route(
        RouteTableId=rt_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )

    ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
    print(f"Route table created and associated: {rt_id}")
    return rt_id


def create_security_group(vpc_id, name):
    # security groups are stateful - allow inbound, outbound response is automatic
    # this is different from NACLs which are stateless
    ec2 = get_ec2_client()
    response = ec2.create_security_group(
        GroupName=name,
        Description='DevOps journey Day 20 security group',
        VpcId=vpc_id
    )
    sg_id = response['GroupId']

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
            },
            {
                'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
            }
        ]
    )

    print(f"Security group created: {sg_id} (SSH + HTTP allowed)")
    return sg_id


def generate_vpc_report(vpc_id, subnets, igw_id, sg_id):
    report = {
        "generated_at": datetime.now().isoformat(),
        "day": "Day 20 of 90",
        "topic": "VPC Deep Dive",
        "vpc_id": vpc_id,
        "vpc_cidr": VPC_CIDR,
        "subnets": subnets,
        "internet_gateway": igw_id,
        "security_group": sg_id
    }
    filename = f"vpc-report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"VPC report saved: {filename}")
    return filename


def cleanup_vpc(vpc_id, subnet_ids, igw_id, sg_id, rt_id):
    ec2 = get_ec2_client()
    try:
        ec2.delete_security_group(GroupId=sg_id)
        print("Security group deleted")

        for subnet_id in subnet_ids:
            ec2.delete_subnet(SubnetId=subnet_id)
            print(f"Subnet deleted: {subnet_id}")

        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)
        print("Internet Gateway deleted")

        # delete route table before VPC
        ec2.delete_route_table(RouteTableId=rt_id)
        print("Route table deleted")

        ec2.delete_vpc(VpcId=vpc_id)
        print(f"VPC deleted: {vpc_id}")

    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == "__main__":
    print("VPC Builder - Day 20 of 90")
    print("=" * 50)

    vpc_id = create_vpc("devops-journey-vpc")

    public_subnet = create_subnet(
        vpc_id, PUBLIC_CIDR, f"{REGION}a", "public-subnet", public=True
    )

    private_subnet = create_subnet(
        vpc_id, PRIVATE_CIDR, f"{REGION}a", "private-subnet", public=False
    )

    igw_id = create_internet_gateway(vpc_id, "devops-igw")

    rt_id = create_route_table(vpc_id, igw_id, public_subnet, "public-rt")

    sg_id = create_security_group(vpc_id, "devops-sg")

    generate_vpc_report(vpc_id, [public_subnet, private_subnet], igw_id, sg_id)

    print("\nCleaning up...")
    cleanup_vpc(vpc_id, [public_subnet, private_subnet], igw_id, sg_id, rt_id)

    print("\nVPC Builder complete!")
