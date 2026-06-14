import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# ── Load .env file ─────────────────────────────────────────
# load_dotenv() reads .env file in current directory
# Without this, os.getenv() won't find our variables
load_dotenv()

# ── Read config from .env ──────────────────────────────────
# os.getenv('KEY', 'default') reads from .env
# If KEY not found → use default value
REGION = os.getenv('AWS_REGION', 'ap-south-1')
TAG_KEY = os.getenv('EC2_TAG_KEY', 'Environment')
TAG_VALUE = os.getenv('EC2_TAG_VALUE', 'dev')
MANAGEMENT_ACCOUNT = os.getenv('MANAGEMENT_ACCOUNT')
ROLE_NAME = os.getenv('ASSUME_ROLE_NAME', 'DevOpsAutomationRole')


def get_session_for_account(account_id, role_name):
    """
    Assume a role in a target AWS account.

    Why AssumeRole?
    → Companies have multiple AWS accounts (dev/staging/prod)
    → You can't directly access another account
    → STS gives temporary credentials to access it

    How it works:
    Step 1: Your account calls sts.assume_role()
    Step 2: STS checks if you're allowed to assume the role
    Step 3: STS returns temporary credentials (valid 1 hour)
    Step 4: You use those credentials to create a new session
    Step 5: That session controls the target account
    """
    # STS = Security Token Service
    # Handles temporary credentials and cross-account access
    sts = boto3.client('sts')

    # Build role ARN (Amazon Resource Name) for target account
    # Format: arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

    try:
        response = sts.assume_role(
            RoleArn=role_arn,
            # RoleSessionName appears in CloudTrail audit logs
            # Helps identify who ran what automation
            RoleSessionName='DevOpsAutomation'
        )

        # Extract temporary credentials from response
        credentials = response['Credentials']

        # Create new session with temporary credentials
        # This session has access to the target account
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            # SessionToken is REQUIRED for temporary credentials
            # Regular IAM users don't need SessionToken
            aws_session_token=credentials['SessionToken'],
            region_name=REGION
        )

        print(f"✅ Assumed role in account: {account_id}")
        return session

    except Exception as e:
        print(f"❌ Could not assume role in {account_id}: {e}")
        return None


def get_ec2_client(session=None):
    """
    Get EC2 client — either default or for specific account.

    If session provided → use that account's credentials
    If no session → use default ~/.aws/credentials
    """
    if session:
        # session.client() uses assumed role credentials
        return session.client('ec2', region_name=REGION)
    else:
        # boto3.client() uses default credentials
        return boto3.client('ec2', region_name=REGION)


def list_all_instances(session=None):
    """
    List ALL EC2 instances with their details.

    describe_instances() response structure:
    {
        'Reservations': [
            {
                'Instances': [
                    {
                        'InstanceId': 'i-xxx',
                        'State': {'Name': 'running'},
                        'Tags': [{'Key': 'Name', 'Value': 'web'}]
                    }
                ]
            }
        ]
    }
    Reservations = how AWS groups instances internally
    Each reservation has one or more instances
    """
    ec2 = get_ec2_client(session)
    response = ec2.describe_instances()

    instances = []

    # Loop through reservations → then instances inside each
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:

            # Extract Name tag
            # instance.get('Tags', []) returns [] if no tags
            name = 'No Name'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']

            instances.append({
                'id': instance['InstanceId'],
                'name': name,
                'type': instance['InstanceType'],
                # State is a dict — we only need the name string
                'state': instance['State']['Name'],
            })

    print(f"\n🖥️  EC2 Instances in {REGION}: {len(instances)}")
    print("=" * 60)

    if not instances:
        print("   No instances found")
    else:
        for i in instances:
            # Choose emoji based on running state
            emoji = "🟢" if i['state'] == 'running' else "🔴"
            print(f"   {emoji} {i['id']}")
            print(f"      Name  : {i['name']}")
            print(f"      Type  : {i['type']}")
            print(f"      State : {i['state']}")
            print(f"      {'─'*40}")

    return instances


def get_instances_by_tag(tag_key, tag_value, session=None):
    """
    Get instances filtered by a specific tag.

    Why filter by tag?
    → In production you have 100s of instances
    → You only want to touch DEV instances — not PROD
    → Tags let you safely target specific instances

    Filters syntax:
    [
        {
            'Name': 'tag:Environment',  ← filter by tag key
            'Values': ['dev']           ← match this value
        }
    ]
    """
    ec2 = get_ec2_client(session)

    response = ec2.describe_instances(
        Filters=[
            {
                # 'tag:KEY' means filter by tag with that key
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )

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
                'state': instance['State']['Name'],
                'type': instance['InstanceType']
            })

    print(f"\n🏷️  Instances tagged {tag_key}={tag_value}: {len(instances)}")
    for i in instances:
        emoji = "🟢" if i['state'] == 'running' else "🔴"
        print(f"   {emoji} {i['id']} | {i['name']} | {i['state']}")

    return instances


def stop_instances(instance_ids, session=None):
    """
    Stop one or more running EC2 instances.

    Instance lifecycle after stop:
    running → stopping → stopped

    Stopped = NO compute charges
    But EBS (storage) still costs money

    instance_ids MUST be a list:
    ✅ ['i-1234567890abcdef0']
    ❌ 'i-1234567890abcdef0'
    """
    if not instance_ids:
        print("⚠️  No instances to stop")
        return False

    ec2 = get_ec2_client(session)

    try:
        response = ec2.stop_instances(InstanceIds=instance_ids)

        print(f"\n⏹️  Stopping {len(instance_ids)} instance(s)...")
        for item in response['StoppingInstances']:
            # PreviousState = state before stop command
            # CurrentState = state after stop command
            prev = item['PreviousState']['Name']
            curr = item['CurrentState']['Name']
            print(f"   ✅ {item['InstanceId']}: {prev} → {curr}")

        return True

    except Exception as e:
        print(f"❌ Error stopping instances: {e}")
        return False


def start_instances(instance_ids, session=None):
    """
    Start one or more stopped EC2 instances.

    Instance lifecycle after start:
    stopped → pending → running
    """
    if not instance_ids:
        print("⚠️  No instances to start")
        return False

    ec2 = get_ec2_client(session)

    try:
        response = ec2.start_instances(InstanceIds=instance_ids)

        print(f"\n▶️  Starting {len(instance_ids)} instance(s)...")
        for item in response['StartingInstances']:
            prev = item['PreviousState']['Name']
            curr = item['CurrentState']['Name']
            print(f"   ✅ {item['InstanceId']}: {prev} → {curr}")

        return True

    except Exception as e:
        print(f"❌ Error starting instances: {e}")
        return False


def generate_ec2_report(instances):
    """
    Generate JSON report of all EC2 instances.

    Useful for:
    → Cost tracking (how many running vs stopped)
    → Audit trails (who has what running)
    → Compliance reports
    """
    # Count by state using list comprehension
    # [i for i in instances if i['state'] == 'running']
    # → creates list of only running instances
    # len() counts them
    running = len([i for i in instances if i['state'] == 'running'])
    stopped = len([i for i in instances if i['state'] == 'stopped'])

    report = {
        "generated_at": datetime.now().isoformat(),
        "day": "Day 17 of 90",
        "topic": "Advanced boto3 EC2 Automation",
        "region": REGION,
        "summary": {
            "total": len(instances),
            "running": running,
            "stopped": stopped
        },
        "instances": instances
    }

    filename = f"ec2-report-{datetime.now().strftime('%Y-%m-%d')}.json"

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📋 Report saved: {filename}")
    print(f"   Total   : {len(instances)}")
    print(f"   Running : {running}")
    print(f"   Stopped : {stopped}")

    return filename


if __name__ == "__main__":
    print("🖥️  EC2 Controller — Day 17 of 90")
    print("=" * 60)
    print(f"Region    : {REGION}")
    print(f"Tag filter: {TAG_KEY}={TAG_VALUE}")

    # Step 1: List all instances (current account)
    all_instances = list_all_instances()

    # Step 2: Filter by tag
    tagged = get_instances_by_tag(TAG_KEY, TAG_VALUE)

    # Step 3: Generate report
    if all_instances:
        generate_ec2_report(all_instances)
    else:
        print("\n💡 No instances found — that's fine!")
        print("   In a real account you would see your instances here")
        print("   The script is working correctly")

    # Step 4: Show multi-account concept
    print("\n🏢 Multi-Account Support:")
    print("   This script supports AssumeRole for multi-account access")
    print("   To use: call get_session_for_account(account_id, role_name)")
    print("   Then pass session to any function above")
    print(f"   Management account: {MANAGEMENT_ACCOUNT}")

    print("\n✅ EC2 Controller complete!")