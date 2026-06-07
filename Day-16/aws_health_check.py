import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read config from .env
REGION = os.getenv('AWS_REGION', 'ap-south-1')


def check_aws_connection():
    """Verify AWS credentials are working."""
    print("\n🔌 Checking AWS connection...")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Connected to AWS!")
        print(f"   Account ID : {identity['Account']}")
        print(f"   User ARN   : {identity['Arn']}")
        return True, identity
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, {}


def check_s3():
    """Check S3 access and list buckets."""
    print("\n🪣 Checking S3...")
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        bucket_count = len(response['Buckets'])
        print(f"✅ S3 accessible — {bucket_count} bucket(s) found")
        for bucket in response['Buckets']:
            print(f"   → {bucket['Name']}")
        return True, bucket_count
    except Exception as e:
        print(f"❌ S3 check failed: {e}")
        return False, 0


def check_ec2():
    """Check EC2 access."""
    print(f"\n🖥️  Checking EC2 in {REGION}...")
    try:
        ec2 = boto3.client('ec2', region_name=REGION)
        response = ec2.describe_instances()
        instance_count = sum(
            len(r['Instances'])
            for r in response['Reservations']
        )
        print(f"✅ EC2 accessible — {instance_count} instance(s) found")
        return True, instance_count
    except Exception as e:
        print(f"❌ EC2 check failed: {e}")
        return False, 0


def check_iam():
    """Check IAM access."""
    print("\n👤 Checking IAM...")
    try:
        iam = boto3.client('iam')
        summary = iam.get_account_summary()
        data = summary['SummaryMap']
        print(f"✅ IAM accessible")
        print(f"   Users   : {data.get('Users', 0)}")
        print(f"   Roles   : {data.get('Roles', 0)}")
        print(f"   Groups  : {data.get('Groups', 0)}")
        return True, data
    except Exception as e:
        print(f"❌ IAM check failed: {e}")
        return False, {}


def generate_report(results):
    """Save health check results to JSON file."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "day": "Day 16 of 90",
        "topic": "AWS CLI + boto3",
        "region": REGION,
        "results": results
    }
    filename = f"aws-health-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📋 Report saved: {filename}")
    print(json.dumps(report, indent=2))
    return filename


if __name__ == "__main__":
    print("🏥 AWS Health Check — Day 16 of 90")
    print("=" * 50)

    results = {}

    connected, identity = check_aws_connection()
    results['connection'] = 'healthy' if connected else 'failed'

    if connected:
        s3_ok, bucket_count = check_s3()
        results['s3'] = 'healthy' if s3_ok else 'failed'
        results['s3_buckets'] = bucket_count

        ec2_ok, instance_count = check_ec2()
        results['ec2'] = 'healthy' if ec2_ok else 'failed'
        results['ec2_instances'] = instance_count

        iam_ok, iam_data = check_iam()
        results['iam'] = 'healthy' if iam_ok else 'failed'

        generate_report(results)

    print("\n✅ Health check complete!")