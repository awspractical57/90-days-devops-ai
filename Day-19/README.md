# 📅 Day 19 — AWS IAM Deep Dive

## 🎯 What is today about?

IAM controls WHO can do WHAT in your AWS account. Today we go deep — users, groups, roles, policies, trust relationships, and security auditing — all automated with Python boto3.

---

## 🏢 How real companies use IAM

| Concept | Real company use case |
|---------|----------------------|
| **Groups** | All developers get same permissions via one group, not individually |
| **Roles** | EC2 instances read S3 automatically without storing credentials |
| **Custom Policies** | Least privilege — exact permissions needed, nothing more |
| **Security Audit** | Automated MFA checks across hundreds of users |

---

## 🤔 Core IAM Concepts

```
IAM = Identity and Access Management

IAM User   = permanent credentials for a real person
IAM Group  = collection of users — assign permissions once, applies to all
IAM Role   = temporary credentials — for AWS services or cross-account access
IAM Policy = JSON document defining exact permissions
```

**Think of it like a company building:**
```
AWS Account = the company building
IAM User    = employee with permanent ID card
IAM Group   = department (all engineers get same access)
IAM Role    = visitor pass — temporary, expires automatically
IAM Policy  = list of doors the card/pass opens
```

---

## 🤔 Policy Types

```
AWS Managed Policy    → created and maintained by Amazon
                         e.g. AmazonS3FullAccess
                         pre-built but sometimes too broad

Customer Managed      → you create it yourself
                         exact permissions needed (least privilege)

Inline Policy          → attached directly to ONE user/role
                         not reusable, tightly coupled
```

---

## 🤔 Trust Policy vs Permission Policy

This is the most confused IAM concept for beginners:

```
Trust Policy (AssumeRolePolicyDocument)
→ WHO can assume this role
→ Example: "ec2.amazonaws.com can assume this role"

Permission Policy (attached via attach_role_policy)
→ WHAT the role can do once assumed
→ Example: "this role can read S3 buckets"

Both are REQUIRED for a role to be useful:
Trust policy without permissions = role nobody can use for anything
Permissions without trust policy = nobody can assume the role
```

---

## 📋 AWS CLI Commands Practiced

```bash
# See current user
aws iam get-user

# List all users
aws iam list-users --output table

# List all groups
aws iam list-groups --output table

# List all roles
aws iam list-roles \
  --query 'Roles[*].[RoleName,CreateDate]' \
  --output table

# Create IAM group
aws iam create-group --group-name DevOpsEngineers

# Attach policy to group
aws iam attach-group-policy \
  --group-name DevOpsEngineers \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create role with trust policy (EC2 can assume it)
aws iam create-role \
  --role-name DevOpsEC2Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach permission policy to role
aws iam attach-role-policy \
  --role-name DevOpsEC2Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

---

## 🐍 Script — iam_manager.py

**What it does:**
```
Gets account summary (users, groups, roles, policies count)
Lists all users with MFA and access key status
Creates IAM group with attached policies
Creates custom least-privilege policy
Creates IAM role for EC2 service
Generates JSON security report
Cleans up all created resources
```

**Key functions explained:**

```python
# Account summary — overview of IAM resources
iam.get_account_summary()
# Returns: Users, Groups, Roles, Policies, MFADevices counts

# Check if user has MFA enabled
iam.list_mfa_devices(UserName=username)
# Empty list = NO MFA = security risk

# Create group and attach AWS managed policy
iam.create_group(GroupName='DevOpsEngineers')
iam.attach_group_policy(
    GroupName='DevOpsEngineers',
    PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
)

# Create custom policy (exact permissions only)
iam.create_policy(
    PolicyName='DevOpsS3ReadPolicy',
    PolicyDocument=json.dumps(policy_dict)  # dict must become JSON string
)

# Create role with trust policy
iam.create_role(
    RoleName='DevOpsEC2Role',
    AssumeRolePolicyDocument=json.dumps(trust_policy)
)
# Then attach permissions separately
iam.attach_role_policy(RoleName='DevOpsEC2Role', PolicyArn=policy_arn)
```

**Security report logic:**
```python
# Check every user for security issues
for user in users:
    mfa = iam.list_mfa_devices(UserName=username)
    if not mfa['MFADevices']:
        issues.append("NO MFA enabled — security risk!")

    keys = iam.list_access_keys(UserName=username)
    if len(keys['AccessKeyMetadata']) > 1:
        issues.append("Multiple access keys — rotate old keys!")
```

**How to run:**
```bash
python3 iam_manager.py
```

**What we found today:**
```
Account Summary:
  Users: 1, Roles: 7, MFA Devices: 1

Security Report:
  devops: NO MFA enabled — security risk!
```

This is a real finding — fix by enabling MFA on the IAM user in AWS Console.

---

## 🧠 Key Lessons from Day 19

> **Lesson 1:** Trust policy and permission policy are different things. Trust policy says WHO can assume a role. Permission policy says WHAT the role can do. Both are required.

> **Lesson 2:** Always follow least privilege. Custom policies with exact permissions are more secure than AWS managed policies like `AmazonS3FullAccess` which grant more than needed.

> **Lesson 3:** Groups are for assigning permissions to multiple users at once. Add/remove users from groups instead of managing individual user policies.

> **Lesson 4:** Automated security audits catch issues humans miss. A script checking MFA status across 100 users takes seconds — manually checking takes hours.

> **Lesson 5:** IAM resource descriptions cannot contain special Unicode characters like em dashes (—). Use regular hyphens (-) in any AWS resource description field.

---

## 🎯 Interview Questions

1. **What is the difference between an IAM user and an IAM role?**
   > An IAM user has permanent credentials (username/password or access keys) tied to a specific person or application. An IAM role has temporary credentials that anyone or anything (with permission) can assume — used for AWS services, cross-account access, or temporary elevated permissions. Roles are more secure because credentials expire automatically.

2. **What is a trust policy in IAM?**
   > A trust policy (AssumeRolePolicyDocument) defines WHO is allowed to assume a role. It's separate from the permission policy which defines WHAT the role can do once assumed. For example, a trust policy might allow `ec2.amazonaws.com` to assume a role, while the permission policy grants S3 read access.

3. **What is the principle of least privilege?**
   > Give users and roles only the exact permissions they need to do their job — nothing more. Instead of attaching `AmazonS3FullAccess`, create a custom policy that only allows `s3:GetObject` and `s3:ListBucket` if that's all that's needed. Reduces damage if credentials are compromised.

4. **How would you audit IAM security across an AWS account?**
   > Use boto3 to loop through all users with `list_users()`, then for each user check `list_mfa_devices()` for MFA status and `list_access_keys()` for key rotation needs. Generate a report flagging users without MFA or with old/multiple access keys. This can run on a schedule for continuous security monitoring.

5. **What is the difference between AWS managed and customer managed policies?**
   > AWS managed policies are created and maintained by Amazon (like `AmazonS3FullAccess`) — convenient but often broader than needed. Customer managed policies are created by you with exact permissions — more secure following least privilege, but require more setup and maintenance.

---

## 🔧 Troubleshooting

| Error | Why | Fix |
|-------|-----|-----|
| `ValidationError` on description | Special Unicode char (em dash —) | Use regular hyphen (-) instead |
| `EntityAlreadyExists` | Resource name already used | Use unique names or delete existing first |
| `NoSuchEntity` on cleanup | Resource was never created | Check earlier step succeeded before cleanup |
| `MalformedPolicyDocument` | Invalid JSON in policy | Validate JSON syntax before passing to boto3 |
| Role creation fails silently | Missing required Service in trust policy | Always include `Service` or `AWS` in Principal |

---

## 📁 Files in This Folder

```
Day-19/
├── README.md          ← This file
├── .env               ← Config (not in GitHub)
├── .gitignore          ← Excludes .env and reports
└── iam_manager.py     ← Full IAM automation script
```

---

## ⬅️ Previous Day
[Day 18 — AWS S3 Advanced: Versioning, Lifecycle, Bucket Policy](../Day-18/)

## ➡️ Next Day
[Day 20 — AWS VPC Deep Dive: Subnets, Routing, Security Groups](../Day-20/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
