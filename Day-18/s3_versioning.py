import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────
load_dotenv()

# ── Config ─────────────────────────────────────────────────
REGION = os.getenv('AWS_REGION', 'ap-south-1')
PREFIX = os.getenv('S3_BUCKET_PREFIX', 'devops-journey')


def get_s3_client():
    """
    Create S3 client.
    boto3.client('s3') connects to AWS S3 service.
    All S3 operations use this client.
    """
    return boto3.client('s3', region_name=REGION)


def create_bucket(bucket_name):
    """
    Create S3 bucket in specified region.

    Note: us-east-1 has different syntax — no LocationConstraint needed.
    All other regions REQUIRE LocationConstraint.
    """
    s3 = get_s3_client()
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            # LocationConstraint tells AWS which region to create in
            # Without this → bucket created in us-east-1 by default
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"✅ Bucket created: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False


def enable_versioning(bucket_name):
    """
    Enable versioning on S3 bucket.

    Once enabled — every upload creates a new version.
    Versions are identified by unique VersionId strings.

    Versioning states:
    → Unversioned (default) = no version history
    → Enabled = keeps all versions
    → Suspended = stops new versions but keeps old ones
    """
    s3 = get_s3_client()
    try:
        # put_bucket_versioning() enables/disables versioning
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                # Status can be 'Enabled' or 'Suspended'
                'Status': 'Enabled'
            }
        )
        print(f"✅ Versioning enabled on: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Error enabling versioning: {e}")
        return False


def check_versioning_status(bucket_name):
    """
    Check if versioning is enabled on a bucket.

    get_bucket_versioning() returns:
    → {} if versioning never enabled
    → {'Status': 'Enabled'} if enabled
    → {'Status': 'Suspended'} if suspended
    """
    s3 = get_s3_client()
    try:
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        # .get('Status', 'Not enabled') returns default if key missing
        status = response.get('Status', 'Not enabled')
        print(f"\n📋 Versioning status for {bucket_name}: {status}")
        return status
    except Exception as e:
        print(f"❌ Error checking versioning: {e}")
        return None


def upload_version(bucket_name, key, content):
    """
    Upload content to S3 — creates new version if versioning enabled.

    key = the filename/path inside the bucket
    content = file content as string

    Returns the VersionId of the uploaded object.
    VersionId is a unique string like 'abc123def456'
    """
    s3 = get_s3_client()
    try:
        response = s3.put_object(
            Bucket=bucket_name,
            # Key = path/filename inside bucket
            Key=key,
            # Body = file content — must be bytes or string
            Body=content.encode('utf-8')
        )
        # VersionId is only returned if versioning is enabled
        version_id = response.get('VersionId', 'N/A')
        print(f"✅ Uploaded '{key}' — VersionId: {version_id}")
        return version_id
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


def list_versions(bucket_name, key):
    """
    List all versions of a specific file.

    list_object_versions() returns:
    → Versions: list of all versions
    → DeleteMarkers: list of delete markers
    → Each version has VersionId, LastModified, Size
    """
    s3 = get_s3_client()
    try:
        response = s3.list_object_versions(
            Bucket=bucket_name,
            # Prefix filters to only show versions of this key
            Prefix=key
        )

        versions = response.get('Versions', [])
        print(f"\n📚 All versions of '{key}':")
        print(f"   Total versions: {len(versions)}")
        print("   " + "─" * 50)

        for v in versions:
            # IsLatest = True only for the most recent version
            latest = "← LATEST" if v['IsLatest'] else ""
            print(f"   VersionId : {v['VersionId']}")
            print(f"   Modified  : {v['LastModified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size      : {v['Size']} bytes {latest}")
            print("   " + "─" * 50)

        return versions
    except Exception as e:
        print(f"❌ Error listing versions: {e}")
        return []


def get_specific_version(bucket_name, key, version_id):
    """
    Download a specific version of a file.

    This is how you RESTORE a previous version.
    Pass the VersionId of the version you want.
    Without VersionId → gets the latest version.
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(
            Bucket=bucket_name,
            Key=key,
            # VersionId specifies WHICH version to download
            VersionId=version_id
        )
        # response['Body'] is a streaming object
        # .read() reads all content
        # .decode('utf-8') converts bytes to string
        content = response['Body'].read().decode('utf-8')
        print(f"\n📥 Retrieved version {version_id}:")
        print(f"   Content: {content}")
        return content
    except Exception as e:
        print(f"❌ Error retrieving version: {e}")
        return None


def delete_specific_version(bucket_name, key, version_id):
    """
    Delete ONE specific version of a file.

    Unlike regular delete — this permanently removes that version.
    Other versions are NOT affected.
    """
    s3 = get_s3_client()
    try:
        s3.delete_object(
            Bucket=bucket_name,
            Key=key,
            # Without VersionId → adds delete marker (soft delete)
            # With VersionId → permanently deletes that version
            VersionId=version_id
        )
        print(f"✅ Deleted version: {version_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting version: {e}")
        return False


def cleanup_bucket(bucket_name):
    """
    Delete all versions and the bucket itself.

    Normal bucket delete fails if bucket has objects.
    With versioning — must delete ALL versions first.
    Then delete all delete markers.
    Then delete the empty bucket.
    """
    s3 = get_s3_client()
    try:
        # List all versions including delete markers
        response = s3.list_object_versions(Bucket=bucket_name)

        # Delete all object versions
        versions = response.get('Versions', [])
        if versions:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': [
                        {'Key': v['Key'], 'VersionId': v['VersionId']}
                        for v in versions
                    ]
                }
            )

        # Delete all delete markers
        markers = response.get('DeleteMarkers', [])
        if markers:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': [
                        {'Key': m['Key'], 'VersionId': m['VersionId']}
                        for m in markers
                    ]
                }
            )

        # Now delete the empty bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"✅ Bucket deleted: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


if __name__ == "__main__":
    # Create unique bucket name with timestamp
    BUCKET = f"{PREFIX}-day18-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    KEY = "config/app-config.json"

    print("📚 S3 Versioning — Day 18 of 90")
    print("=" * 60)

    # Step 1: Create bucket
    if not create_bucket(BUCKET):
        exit(1)

    # Step 2: Enable versioning
    enable_versioning(BUCKET)
    check_versioning_status(BUCKET)

    # Step 3: Upload 3 versions of same file
    print(f"\n📤 Uploading 3 versions of '{KEY}'...")

    v1_id = upload_version(BUCKET, KEY, json.dumps({
        "version": 1,
        "env": "production",
        "debug": False,
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    v2_id = upload_version(BUCKET, KEY, json.dumps({
        "version": 2,
        "env": "production",
        "debug": True,   # changed this
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    v3_id = upload_version(BUCKET, KEY, json.dumps({
        "version": 3,
        "env": "production",
        "debug": False,
        "max_connections": 100,  # added this
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    # Step 4: List all versions
    versions = list_versions(BUCKET, KEY)

    # Step 5: Retrieve specific old version
    if v1_id:
        print(f"\n🔄 Restoring v1 (simulating rollback)...")
        get_specific_version(BUCKET, KEY, v1_id)

    # Step 6: Clean up
    print(f"\n🧹 Cleaning up...")
    cleanup_bucket(BUCKET)

    print("\n✅ S3 Versioning complete!")