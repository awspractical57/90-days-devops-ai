import boto3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load .env — reads AWS_REGION and AWS_ACCOUNT_ID
load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')


def get_iam_client():
    """
    Create IAM client.
    IAM is a global service — no region needed.
    But we pass region for consistency.
    """
    return boto3.client('iam')


def get_account_summary():
    """
    Get overview of IAM resources in account.

    get_account_summary() returns counts of:
    → Users, Groups, Roles, Policies
    → MFA devices, Access keys
    Useful for security audits.
    """
    iam = get_iam_client()
    response = iam.get_account_summary()
    data = response['SummaryMap']

    print("\n📊 IAM Account Summary:")
    print("=" * 50)
    print(f"   Users          : {data.get('Users', 0)}")
    print(f"   Groups         : {data.get('Groups', 0)}")
    print(f"   Roles          : {data.get('Roles', 0)}")
    print(f"   Policies       : {data.get('Policies', 0)}")
    print(f"   MFA Devices    : {data.get('MFADevices', 0)}")
    print(f"   Access Keys    : {data.get('AccountAccessKeysPresent', 0)}")
    return data


def list_users_with_details():
    """
    List all IAM users with their access keys and MFA status.

    list_users() returns basic user info.
    list_access_keys() shows if user has CLI access.
    list_mfa_devices() shows if MFA is enabled.

    Security check: users without MFA = security risk.
    """
    iam = get_iam_client()
    response = iam.list_users()
    users = response['Users']

    print(f"\n👤 IAM Users ({len(users)} total):")
    print("=" * 50)

    for user in users:
        username = user['UserName']

        # Check access keys
        # list_access_keys() returns keys for specified user
        keys_response = iam.list_access_keys(UserName=username)
        key_count = len(keys_response['AccessKeyMetadata'])

        # Check MFA devices
        # list_mfa_devices() returns MFA devices for user
        mfa_response = iam.list_mfa_devices(UserName=username)
        mfa_enabled = len(mfa_response['MFADevices']) > 0

        # Security indicators
        mfa_status = "✅ MFA on" if mfa_enabled else "⚠️  NO MFA"
        key_status = f"🔑 {key_count} key(s)"

        print(f"\n   User     : {username}")
        print(f"   Created  : {user['CreateDate'].strftime('%Y-%m-%d')}")
        print(f"   MFA      : {mfa_status}")
        print(f"   Keys     : {key_status}")

    return users


def create_iam_group(group_name, policy_arns):
    """
    Create IAM group and attach policies.

    Groups let you assign same permissions to multiple users.
    Instead of attaching policies to each user individually
    → attach to group → add users to group.

    policy_arns = list of policy ARNs to attach
    ARN format: arn:aws:iam::aws:policy/PolicyName
    """
    iam = get_iam_client()

    try:
        # create_group() creates the group
        iam.create_group(GroupName=group_name)
        print(f"\n✅ Group created: {group_name}")

        # Attach each policy to the group
        for policy_arn in policy_arns:
            iam.attach_group_policy(
                GroupName=group_name,
                # PolicyArn = Amazon Resource Name of the policy
                PolicyArn=policy_arn
            )
            # Extract just policy name from ARN for display
            policy_name = policy_arn.split('/')[-1]
            print(f"   ✅ Attached: {policy_name}")

        return True
    except Exception as e:
        print(f"❌ Error creating group: {e}")
        return False


def create_custom_policy(policy_name, policy_document):
    """
    Create a custom IAM policy.

    Custom policies let you define exact permissions needed.
    More secure than AWS managed policies (least privilege).

    policy_document = dict describing permissions
    Must be converted to JSON string for AWS API.
    """
    iam = get_iam_client()

    try:
        response = iam.create_policy(
            PolicyName=policy_name,
            # json.dumps() converts Python dict to JSON string
            # AWS API requires JSON string not Python dict
            PolicyDocument=json.dumps(policy_document),
            Description=f'Custom policy created by Day 19 automation'
        )
        policy_arn = response['Policy']['Arn']
        print(f"\n✅ Custom policy created: {policy_name}")
        print(f"   ARN: {policy_arn}")
        return policy_arn
    except Exception as e:
        print(f"❌ Error creating policy: {e}")
        return None


def create_role_for_service(role_name, service, policy_arns):
    """
    Create IAM role for an AWS service.

    Roles let AWS services act on your behalf.
    Example: EC2 instance reads S3 → needs role with S3 access.

    Trust policy = who can ASSUME this role
    For EC2: {"Service": "ec2.amazonaws.com"}
    For Lambda: {"Service": "lambda.amazonaws.com"}
    """
    iam = get_iam_client()

    # Trust policy = who can assume this role
    # This is DIFFERENT from permissions policy
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                # Principal = who can assume this role
                # Service = an AWS service (ec2, lambda, etc)
                "Principal": {"Service": f"{service}.amazonaws.com"},
                # sts:AssumeRole = the action of assuming a role
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        response = iam.create_role(
            RoleName=role_name,
            # AssumeRolePolicyDocument = trust policy
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f'Role for {service} - Day 19 automation'
        )
        print(f"\n✅ Role created: {role_name}")
        print(f"   Service: {service}.amazonaws.com")

        # Attach permission policies to the role
        for policy_arn in policy_arns:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            policy_name = policy_arn.split('/')[-1]
            print(f"   ✅ Attached: {policy_name}")

        return response['Role']['Arn']
    except Exception as e:
        print(f"❌ Error creating role: {e}")
        return None


def generate_iam_security_report():
    """
    Generate security report of IAM configuration.

    Checks for common security issues:
    → Users without MFA
    → Users with multiple access keys
    → Root account usage
    Saves report to JSON file.
    """
    iam = get_iam_client()

    report = {
        "generated_at": datetime.now().isoformat(),
        "day": "Day 19 of 90",
        "topic": "IAM Security Report",
        "findings": [],
        "users": []
    }

    # Check each user for security issues
    users = iam.list_users()['Users']
    for user in users:
        username = user['UserName']
        issues = []

        # Check MFA
        mfa = iam.list_mfa_devices(UserName=username)
        if not mfa['MFADevices']:
            issues.append("NO MFA enabled — security risk!")

        # Check access keys
        keys = iam.list_access_keys(UserName=username)
        if len(keys['AccessKeyMetadata']) > 1:
            issues.append("Multiple access keys — rotate old keys!")

        user_report = {
            "username": username,
            "created": user['CreateDate'].isoformat(),
            "mfa_enabled": len(mfa['MFADevices']) > 0,
            "access_key_count": len(keys['AccessKeyMetadata']),
            "security_issues": issues
        }
        report["users"].append(user_report)

        if issues:
            report["findings"].extend(
                [f"{username}: {issue}" for issue in issues]
            )

    # Save report
    filename = f"iam-report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📋 IAM Security Report: {filename}")
    print(f"   Users checked : {len(users)}")
    print(f"   Findings      : {len(report['findings'])}")
    for finding in report['findings']:
        print(f"   ⚠️  {finding}")

    return report


def cleanup(group_name, role_name, policy_arn):
    """Clean up created resources."""
    iam = get_iam_client()

    try:
        # Detach and delete group
        policies = iam.list_attached_group_policies(
            GroupName=group_name
        )['AttachedPolicies']
        for p in policies:
            iam.detach_group_policy(
                GroupName=group_name,
                PolicyArn=p['PolicyArn']
            )
        iam.delete_group(GroupName=group_name)
        print(f"✅ Group deleted: {group_name}")

        # Detach and delete role
        role_policies = iam.list_attached_role_policies(
            RoleName=role_name
        )['AttachedPolicies']
        for p in role_policies:
            iam.detach_role_policy(
                RoleName=role_name,
                PolicyArn=p['PolicyArn']
            )
        iam.delete_role(RoleName=role_name)
        print(f"✅ Role deleted: {role_name}")

        # Delete custom policy
        if policy_arn:
            iam.delete_policy(PolicyArn=policy_arn)
            print(f"✅ Policy deleted")

    except Exception as e:
        print(f"❌ Cleanup error: {e}")


if __name__ == "__main__":
    print("🔐 IAM Manager — Day 19 of 90")
    print("=" * 50)

    # Step 1: Account summary
    get_account_summary()

    # Step 2: List users with security details
    list_users_with_details()

    # Step 3: Create group with policies
    GROUP = "DevOpsEngineers"
    create_iam_group(GROUP, [
        "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
        "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
    ])

    # Step 4: Create custom S3 read policy
    POLICY_NAME = "DevOpsS3ReadPolicy"
    custom_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowS3Read",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:GetBucketLocation"
                ],
                # * = applies to ALL S3 buckets
                "Resource": "*"
            }
        ]
    }
    policy_arn = create_custom_policy(POLICY_NAME, custom_policy)

    # Step 5: Create EC2 role
    ROLE_NAME = "DevOpsEC2S3Role"
    create_role_for_service(ROLE_NAME, "ec2", [
        "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
    ])

    # Step 6: Security report
    generate_iam_security_report()

    # Step 7: Cleanup
    print("\n🧹 Cleaning up...")
    cleanup(GROUP, ROLE_NAME, policy_arn)

    print("\n✅ IAM Manager complete!")
