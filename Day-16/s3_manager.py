import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
PREFIX = os.getenv('S3_BUCKET_PREFIX', 'devops-journey')


def list_all_buckets():
    """List all S3 buckets."""
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = response.get('Buckets', [])
    print(f"\n📦 Your S3 buckets ({len(buckets)} total):")
    for bucket in buckets:
        created = bucket['CreationDate'].strftime('%Y-%m-%d')
        print(f"   → {bucket['Name']} (created: {created})")
    return buckets


def create_bucket(bucket_name):
    """Create a new S3 bucket."""
    s3 = boto3.client('s3', region_name=REGION)
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"✅ Bucket created: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False


def upload_file(bucket_name, content, filename):
    """Upload content to S3."""
    s3 = boto3.client('s3')
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=content.encode('utf-8')
        )
        print(f"✅ Uploaded: {filename} to {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def list_files(bucket_name):
    """List files in a bucket."""
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])
        print(f"\n📁 Files in {bucket_name}:")
        for obj in objects:
            print(f"   → {obj['Key']} ({obj['Size']} bytes)")
        return objects
    except Exception as e:
        print(f"❌ List failed: {e}")
        return []


def download_file(bucket_name, filename):
    """Download a file from S3."""
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        content = response['Body'].read().decode('utf-8')
        print(f"✅ Downloaded: {filename}")
        print(f"   Content preview: {content[:150]}")
        return content
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def delete_bucket(bucket_name):
    """Delete bucket and all contents."""
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])
        if objects:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': [{'Key': obj['Key']} for obj in objects]
                }
            )
        s3.delete_bucket(Bucket=bucket_name)
        print(f"✅ Bucket deleted: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Delete failed: {e}")
        return False


if __name__ == "__main__":
    BUCKET = f"{PREFIX}-day16-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    print("🪣 S3 Manager — Day 16 of 90")
    print("=" * 50)

    list_all_buckets()

    print(f"\nCreating bucket: {BUCKET}")
    if create_bucket(BUCKET):

        content = json.dumps({
            "day": 16,
            "topic": "boto3 S3 automation",
            "timestamp": datetime.now().isoformat(),
            "message": "Created automatically with Python boto3!"
        }, indent=2)
        upload_file(BUCKET, content, "day16-report.json")

        list_files(BUCKET)

        download_file(BUCKET, "day16-report.json")

        print("\n🧹 Cleaning up...")
        delete_bucket(BUCKET)

    print("\n✅ S3 Manager complete!")
