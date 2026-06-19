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


def apply_lifecycle_policy(bucket_name):
    """
    Apply lifecycle policy to automatically manage object storage.

    Lifecycle rules control what happens to objects over time:

    Transitions: move objects to cheaper storage class
    → STANDARD_IA after 30 days  = 46% cheaper than Standard
    → GLACIER after 90 days      = 83% cheaper than Standard

    Expiration: delete objects after X days
    → Delete after 365 days = never pay for year-old logs

    NoncurrentVersionExpiration: delete old versions
    → Delete old versions after 30 days
    → Keeps costs low for versioned buckets
    """
    s3 = boto3.client('s3', region_name=REGION)

    # Lifecycle configuration is a dict with 'Rules' list
    lifecycle_config = {
        'Rules': [
            {
                # ID = unique name for this rule
                'ID': 'DevOpsJourneyLifecycle',
                # Status = 'Enabled' or 'Disabled'
                'Status': 'Enabled',
                # Filter = which objects this rule applies to
                # Empty Prefix = applies to ALL objects in bucket
                'Filter': {'Prefix': ''},
                # Transitions = move to cheaper storage after X days
                'Transitions': [
                    {
                        # After 30 days → move to Infrequent Access
                        # 46% cheaper, slight retrieval fee
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'
                    },
                    {
                        # After 90 days → move to Glacier
                        # 83% cheaper, takes minutes to retrieve
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ],
                # Expiration = delete objects after X days
                'Expiration': {
                    'Days': 365  # delete after 1 year
                },
                # NoncurrentVersionExpiration = delete old versions
                # Only applies if versioning is enabled
                'NoncurrentVersionExpiration': {
                    'NoncurrentDays': 30  # keep old versions 30 days
                }
            },
            {
                # Second rule: specific to logs/ folder
                'ID': 'LogsCleanup',
                'Status': 'Enabled',
                'Filter': {
                    # Prefix = only apply to objects starting with logs/
                    'Prefix': 'logs/'
                },
                'Expiration': {
                    'Days': 7  # delete logs after 7 days
                }
            }
        ]
    }

    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_config
        )
        print(f"✅ Lifecycle policy applied to: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Error applying lifecycle: {e}")
        return False


def get_lifecycle_policy(bucket_name):
    """
    Read and display current lifecycle policy.

    get_bucket_lifecycle_configuration() returns the policy
    that was applied with put_bucket_lifecycle_configuration()
    """
    s3 = boto3.client('s3', region_name=REGION)
    try:
        response = s3.get_bucket_lifecycle_configuration(
            Bucket=bucket_name
        )

        print(f"\n📋 Lifecycle policy on {bucket_name}:")
        print("=" * 60)

        for rule in response['Rules']:
            print(f"\n   Rule ID : {rule['ID']}")
            print(f"   Status  : {rule['Status']}")

            # Show transitions if they exist
            for t in rule.get('Transitions', []):
                print(f"   Day {t['Days']:3d} → Move to {t['StorageClass']}")

            # Show expiration if it exists
            if 'Expiration' in rule:
                print(f"   Day {rule['Expiration']['Days']:3d} → DELETE permanently")

            # Show old version cleanup
            if 'NoncurrentVersionExpiration' in rule:
                days = rule['NoncurrentVersionExpiration']['NoncurrentDays']
                print(f"   Old versions → DELETE after {days} days")

        return response['Rules']
    except Exception as e:
        print(f"❌ Error getting lifecycle: {e}")
        return []


def calculate_storage_savings(size_gb, months=12):
    """
    Calculate storage cost savings from lifecycle policy.

    Shows real cost comparison over time.
    Prices are approximate AWS ap-south-1 rates.
    """
    # Storage costs per GB per month
    standard_cost = 0.023      # S3 Standard
    ia_cost = 0.0125           # S3 Standard-IA
    glacier_cost = 0.004       # S3 Glacier

    # Without lifecycle: all data stays in Standard
    cost_without = size_gb * standard_cost * months

    # With lifecycle:
    # Month 1: Standard
    # Months 2-3: Standard-IA
    # Months 4-12: Glacier
    cost_with = (
        size_gb * standard_cost * 1 +    # 1 month Standard
        size_gb * ia_cost * 2 +          # 2 months IA
        size_gb * glacier_cost * 9       # 9 months Glacier
    )

    savings = cost_without - cost_with
    savings_pct = (savings / cost_without) * 100

    print(f"\n💰 Storage Cost Analysis for {size_gb}GB over {months} months:")
    print("=" * 60)
    print(f"   Without lifecycle : ${cost_without:.2f}")
    print(f"   With lifecycle    : ${cost_with:.2f}")
    print(f"   Savings           : ${savings:.2f} ({savings_pct:.0f}%)")

    return savings


def upload_sample_files(bucket_name):
    """
    Upload sample files to demonstrate lifecycle policy.
    """
    s3 = boto3.client('s3', region_name=REGION)

    files = {
        "config/app.json": '{"env": "production", "version": "1.0"}',
        "logs/app-2026-06-01.log": "2026-06-01 ERROR: Connection timeout",
        "logs/app-2026-06-02.log": "2026-06-02 INFO: Server started",
        "reports/monthly-report.json": '{"month": "June", "total": 1500}',
        "backups/backup-2026-06.tar": "backup data here"
    }

    print(f"\n📤 Uploading sample files...")
    for key, content in files.items():
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content.encode('utf-8')
        )
        print(f"   ✅ {key}")


def list_bucket_contents(bucket_name):
    """
    List all files showing size and storage class.
    """
    s3 = boto3.client('s3', region_name=REGION)
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])

        print(f"\n📁 Contents of {bucket_name}:")
        print("=" * 60)
        for obj in objects:
            size = obj['Size']
            # StorageClass shows current storage tier
            storage = obj.get('StorageClass', 'STANDARD')
            print(f"   {obj['Key']}")
            print(f"   → Size: {size} bytes | Storage: {storage}")

        return objects
    except Exception as e:
        print(f"❌ Error listing: {e}")
        return []


def cleanup_bucket(bucket_name):
    """Delete all objects and the bucket."""
    s3 = boto3.client('s3', region_name=REGION)
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])
        if objects:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': [{'Key': o['Key']} for o in objects]}
            )
        s3.delete_bucket(Bucket=bucket_name)
        print(f"✅ Bucket deleted: {bucket_name}")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")


if __name__ == "__main__":
    BUCKET = f"{PREFIX}-lifecycle-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    print("♻️  S3 Lifecycle Policy — Day 18 of 90")
    print("=" * 60)

    # Step 1: Create bucket
    if not create_bucket(BUCKET):
        exit(1)

    # Step 2: Upload sample files
    upload_sample_files(BUCKET)

    # Step 3: Apply lifecycle policy
    apply_lifecycle_policy(BUCKET)

    # Step 4: Verify policy applied
    get_lifecycle_policy(BUCKET)

    # Step 5: List bucket contents
    list_bucket_contents(BUCKET)

    # Step 6: Calculate savings (100GB example)
    calculate_storage_savings(size_gb=100, months=12)

    # Step 7: Clean up
    print(f"\n🧹 Cleaning up...")
    cleanup_bucket(BUCKET)

    print("\n✅ S3 Lifecycle complete!")
