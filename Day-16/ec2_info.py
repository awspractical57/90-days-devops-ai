import boto3
import os
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')


def list_instances():
    """List all EC2 instances."""
    ec2 = boto3.client('ec2', region_name=REGION)
    response = ec2.describe_instances()

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = 'No Name'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']
            instances.append({
                'id': instance['InstanceId'],
                'name': name,
                'type': instance['InstanceType'],
                'state': instance['State']['Name'],
            })

    print(f"\n🖥️  EC2 Instances in {REGION}: {len(instances)}")
    print("=" * 50)
    if instances:
        for i in instances:
            print(f"   ID    : {i['id']}")
            print(f"   Name  : {i['name']}")
            print(f"   Type  : {i['type']}")
            print(f"   State : {i['state']}")
            print(f"   {'-'*30}")
    else:
        print("   No instances found — none running yet")
    return instances


def list_vpcs():
    """List all VPCs."""
    ec2 = boto3.client('ec2', region_name=REGION)
    response = ec2.describe_vpcs()
    print(f"\n🌐 VPCs in {REGION}:")
    print("=" * 50)
    for vpc in response['Vpcs']:
        default = "DEFAULT" if vpc['IsDefault'] else "custom"
        print(f"   → {vpc['VpcId']} | {vpc['CidrBlock']} | {default}")
    return response['Vpcs']


def list_security_groups():
    """List all security groups."""
    ec2 = boto3.client('ec2', region_name=REGION)
    response = ec2.describe_security_groups()
    print(f"\n🔒 Security Groups in {REGION}:")
    print("=" * 50)
    for sg in response['SecurityGroups']:
        print(f"   → {sg['GroupId']} | {sg['GroupName']}")
    return response['SecurityGroups']


if __name__ == "__main__":
    print("🖥️  EC2 Info — Day 16 of 90")
    print("=" * 50)

    list_instances()
    list_vpcs()
    list_security_groups()

    print("\n✅ EC2 Info complete!")
