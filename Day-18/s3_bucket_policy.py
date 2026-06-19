import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
PREFIX = os.getenv('S3_BUCKET_PREFIX', 'devops-journey')


def create_bucket(bucket_name):
    """Create S3 bucket."""
    s3 = boto3.client('s3', region_name=REGION)
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"✅ Bucket created: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def apply_read_only_policy(bucket_name, account_id):
    """
    Apply policy that allows only READ access.

    Bucket Policy is a JSON document with:
    → Version: policy language version (always use 2012-10-17)
    → Statement: list of permission rules

    Each Statement has:
    → Sid: unique name for this statement
    → Effect: 'Allow' or 'Deny'
    → Principal: WHO this applies to (* = everyone)
    → Action: WHAT they can do (s3:GetObject = read files)
    → Resource: WHICH resources (arn:aws:s3:::bucket/*)
    """
    s3 = boto3.client('s3', region_name=REGION)

    # Build the policy as a Python dict
    policy = {
        # Version is always this value — it's the policy language version
        "Version": "2012-10-17",
        "Statement": [
            {
                # Sid = Statement ID — unique name for this rule
                "Sid": "AllowAccountReadOnly",
                # Effect = what happens when rule matches
                "Effect": "Allow",
                # Principal = who this applies to
                # AWS account ID = only your account can access
                "Principal": {
                    "AWS": f"arn:aws:iam::{account_id}:root"
                },
                # Action = what operations are allowed
                # s3:GetObject = download/read files
                # s3:ListBucket = see list of files
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                # Resource = which S3 resources this applies to
                # arn:aws:s3:::bucket = the bucket itself
                # arn:aws:s3:::bucket/* = all objects inside
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            },
            {
                "Sid": "DenyDelete",
                # Deny = explicitly block this action
                # Deny ALWAYS wins over Allow
                "Effect": "Deny",
                # * = applies to everyone including account owner
                "Principal": "*",
                # s3:DeleteObject = cannot delete files
                "Action": "s3:DeleteObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }

    try:
        s3.put_bucket_policy(
            Bucket=bucket_name,
            # Policy must be a JSON STRING not a dict
            # json.dumps() converts dict to JSON string
            Policy=json.dumps(policy)
        )
        print(f"✅ Bucket policy applied")
        return True
    except Exception as e:
        print(f"❌ Error applying policy: {e}")
        return False


def get_bucket_policy(bucket_name):
    """
    Read current bucket policy.
    """
    s3 = boto3.client('s3', region_name=REGION)
    try:
        response = s3.get_bucket_policy(Bucket=bucket_name)
        # Policy is returned as JSON string — parse it back to dict
        policy = json.loads(response['Policy'])

        print(f"\n📋 Current bucket policy:")
        print("=" * 60)
        for statement in policy['Statement']:
            print(f"\n   Sid    : {statement.get('Sid', 'N/A')}")
            print(f"   Effect : {statement['Effect']}")
            print(f"   Action : {statement['Action']}")
        return policy
    except Exception as e:
        print(f"❌ Error getting policy: {e}")
        return None


def show_policy_examples():
    """
    Show common bucket policy examples for learning.
    These are NOT applied — just for reference.
    """
    print("\n📚 Common Bucket Policy Examples:")
    print("=" * 60)

    examples = {
        "1. Public read (website hosting)": {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*"
        },
        "2. Deny non-HTTPS access": {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Condition": {
                "Bool": {"aws:SecureTransport": "false"}
            }
        },
        "3. Allow specific IAM user only": {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789:user/devops"
            },
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    }

    for name, policy in examples.items():
        print(f"\n   {name}:")
        print(f"   {json.dumps(policy, indent=4)}")


def cleanup_bucket(bucket_name):
    """Delete bucket policy, objects, and bucket."""
    s3 = boto3.client('s3', region_name=REGION)
    try:
        # Delete policy first
        s3.delete_bucket_policy(Bucket=bucket_name)
        # Delete objects
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])
        if objects:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': [{'Key': o['Key']} for o in objects]}
            )
        # Delete bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"✅ Bucket deleted: {bucket_name}")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")


if __name__ == "__main__":
    BUCKET = f"{PREFIX}-policy-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    print("🔒 S3 Bucket Policy — Day 18 of 90")
    print("=" * 60)

    # Get account ID for policy
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    print(f"Account ID: {account_id}")

    # Step 1: Create bucket
    if not create_bucket(BUCKET):
        exit(1)

    # Step 2: Apply read-only policy
    apply_read_only_policy(BUCKET, account_id)

    # Step 3: Read back the policy
    get_bucket_policy(BUCKET)

    # Step 4: Show policy examples
    show_policy_examples()

    # Step 5: Clean up
    print(f"\n🧹 Cleaning up...")
    cleanup_bucket(BUCKET)

    print("\n✅ S3 Bucket Policy complete!")
