import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION','ap-south-1')
PREFIX = os.getenv('S3_BUCKET_PREFIX','devops-journey')

def get_s3_client():
    """
    Create S3 client.
    boto3.client('s3') connects to AWS S3 service.
    All S3 Operations use this client.
    """

    return boto3.client('s3', region_name=REGION)

def create_bucket(bucket_name):
    """
    Create S3 bucket in specified region.

    Note: us-east-1 has different syntax - no LocationConstraint needed.
    All other regions REQUIRE LocationConstraint.
    """
    s3 = get_s3_client()
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"Bucket created:{bucket_name}")
        return True
    except Exception as e:
        print(f"Error creating bucket: {e}")
        return False
def enable_versioning(bucket_name):
    """
    Enable versioning on S3 bucket.
    
    Once enabled -every upload creates a new version.
    Versions are identified by unique VersionId strings.

    Versioning states:
    -> Unversioned (default) = no version history
    -> Enabled = keeps all versions
    -> Suspended = stops new versions but keeps old ones
    """
    s3 = get_s3_client()
    try:
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                'Status':'Enabled'
            }
        )
        print(f"Versioning enabled on: {bucket_name}")
        return True
    except Exception as e:
        print(f"Error enabling versioning: {e}")
        return False
    
def check_versioning_status(bucket_name):
    """
    Check if versioning is enabled on a bucket.

    get_bucket_versioning() returns:
    -> {} if versioning never enabled
    -> {'Status': 'Enabled'} if enabled
    -> {'Status': 'Suspended'} if suspended
    """
    s3 = get_s3_client()
    try:
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        status = response.get('Status', 'Not enabled')
        print(f"\n Versioning status for {bucket_name}:{status}")
        return status
    except Exception as e:
        print(f"Error checking versioning: {e}")
        return None
def upload_version(bucket_name, key, content):
    """
    Upload content to S3 - create new version if versioning enabled.

    Key = the filename/path inside the bucket
    content = file content as string

    Returns the VersionId of the uploaded object.
    VersionId is a unique string like 'abc123def456'
    """
    s3 = get_s3_client()
    try:
        response = s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content.encode('utf-8')
        )
        version_id = response.get('VersionId', 'N/A')
        print(f"Uploaded '{key} - VersionId: {version_id}")
        return version_id
    except Exception as e:
        print(f"Upload failed: {e}")
        return None
def list_versions(bucket_name, key):
    """
    List all versions of a specific file.

    list_object_versions() returns:
    -> Versions: list of all versions
    -> DeleteMarkers: list of delete markers
    -> Each version has versionId, LastModified, Size
    """
    s3 = get_s3_client()
    try:
        response = s3.list_object_versions(
            Bucket=bucket_name,
            Prefix=key
        )

        versions = response.get('Versions',[])
        print(f"\n All versions of '{key}':")
        print(f"    Total versions: {len(versions)}")
        print("    "+"-" * 50)

        for v in versions:
            latest = "<- LATEST" if v['IsLatest'] else ""
            print(f"    VersionId : {v['VersionId']}")
            print(f"    Modified : {v['LastModified'].strftime('%Y-%m-%d %H:%M:%s')}")
            print(f"    Size : {v['Size']} bytes {latest}")
            print("    " + "-" * 50)
        return versions
    except Exception as e:
        print(f"Error listing versions: {e}")
        return []

def get_specific_version(bucket_name, key, version_id):
    """
    Download a specific version of a file.
    This is how you RESTORE a previous version.
    Pass the VersionId of the version you want.
    Without VersionId -> gets the latest version.
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(
            Bucket=bucket_name,
            Key=key,
            versionId=version_id
        )
        content = response['Body'].read().decode('utf-8')
        print(f"\n Retrieved version {version_id}:")
        print(f"    Content: {content}")
        return content
    except Exception as e:
        print(f"Error retrieving version: {e}")
        return None
    
def delete_specific_version(bucket_name, key, version_id):
    """
    Delete ONE specific version of a file.

    Unlike regular delete - this permanently removes that version.
    Other versions are NOT affected.
    """
    s3 = get_s3_client()
    try:
        s3.delete_object(
            Bucket=bucket_name,
            Key=key,
            VersionId=version_id
        )
        print(f"Deleted version: {version_id}")
        return True
    except Exception as e:
        print(f"Error deleting version: {e}")
        return False
    
def cleanup_bucket(bucket_name):
    """
    Delete all versions and the bucket itself.

    Nornal bucket delete fails if bucket has objects.
    With versioning - must delete ALL versions first.
    Then delete all delete markers.
    Then delete the empty bucket.
    """
    s3 = get_s3_client()
    try:
        response = s3.list_object_versions(Bucket=bucket_name)

        versions = response.get('Versions',[])
        if versions:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects':[
                        {'Key': v['Key'], 'VersionId': v['VersionId']}
                        for v in versions
                    ]
                }
            )
        
        markers = response.get('DeleteMarkers',[])
        if markers:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects':[
                        {'Key': m['Key'], 'VersionId': m['VersionId']}
                        for m in markers
                    ]
                }
            )
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Bucket deleted: {bucket_name}")
        return True
    except Exception as e:
        print(f"Cleanup failed: {e}")
        return False

if __name__ == "__main__":
    BUCKET = f"{PREFIX}-day18-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    KEY = "config/app-config.json"

    print("S3 versioning - Day 18 of 90")
    print("=" * 60)

    if not create_bucket(BUCKET):
        exit(1)
    
    enable_versioning(BUCKET)
    check_versioning_status(BUCKET)

    print(f"\n Uploading 3 versions of '{KEY}'....")

    v1_id = upload_version(BUCKET, KEY, json.dumps({
        "version": 1,
        "env": "production",
        "debug": False,
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    v2_id = upload_version(BUCKET, KEY, json.dumps({
        "version": 2,
        "env":"production",
        "dedug": True,
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    v3_id = upload_version(BUCKET, KEY, json.dumps({
        "version": 3,
        "env": "prodution",
        "debug": False,
        "max_connections": 100,
        "timestamp": datetime.now().isoformat()
    }, indent=2))

    versions = list_versions(BUCKET, KEY)

    if v1_id:
        print(f"\n Restoring v1 (simulating rollback)....")
        get_specific_version(BUCKET, KEY, v1_id)

    print(f"\n Cleaning up...")
    cleanup_bucket(BUCKET)

    print ("\n S3 Versioning complete!")
    



