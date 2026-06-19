# 📅 Day 18 — AWS S3 Advanced: Versioning, Lifecycle & Bucket Policy

## 🎯 What is today about?

Day 16 we learned basic S3 — create, upload, download, delete.
Today we go advanced — versioning, lifecycle policies, and bucket policies.

By the end of today we automated all 3 features with Python boto3 scripts, explained line by line for beginners.

---

## 🏢 How real companies use these features

| Feature | Real company use case |
|---------|----------------------|
| **Versioning** | Netflix versions every config file — bad deploy? roll back in 30 seconds |
| **Lifecycle** | Spotify moves old audio logs to Glacier automatically — saves millions |
| **Bucket Policy** | Airbnb allows CloudFront to read S3 but blocks direct public access |

---

## 🤔 Concept 1 — What is S3 Versioning?

**Problem without versioning:**
```
Upload report.pdf → v1
Upload report.pdf again → v2 OVERWRITES v1
v1 is GONE forever — no recovery possible
One wrong upload = permanent data loss
```

**With versioning enabled:**
```
Upload report.pdf → v1 saved with unique VersionId
Upload report.pdf again → v2 saved, v1 still exists
Delete report.pdf → delete marker added, file NOT actually gone
Restore anytime → retrieve any previous VersionId
```

**Versioning states:**
```
Unversioned (default) → no history kept
Enabled               → all versions kept forever
Suspended             → stops new versions, keeps old ones
```

**What we proved today:**
```
Uploaded test.txt 3 times to same key
aws s3api list-object-versions showed:
→ Version 3: e4kdHiL0... (latest)
→ Version 2: efwAoy1F...
→ Version 1: z1UZMtKm... (oldest — still accessible!)
```

---

## 🤔 Concept 2 — What are Lifecycle Policies?

**Problem:**
```
Log files uploaded daily → after 1 year = 365 files
Old logs rarely accessed but still cost full price
Manual cleanup wastes engineering time
```

**Solution — Lifecycle Policy:**
```
Rule: Move objects to cheaper storage automatically

Day 0-29:   S3 Standard     → $0.023/GB  (frequent access)
Day 30-89:  S3 Standard-IA  → $0.0125/GB (46% cheaper)
Day 90-364: S3 Glacier      → $0.004/GB  (83% cheaper)
Day 365+:   DELETE          → $0.00/GB   (gone forever)
```

**Real savings on 100GB over 12 months:**
```
Without lifecycle: $27.60
With lifecycle:    $8.27
Savings:           $19.33 (70% saved) — zero manual work
```

**Lifecycle policy JSON structure:**
```json
{
    "Rules": [
        {
            "ID": "DevOpsJourneyLifecycle",
            "Status": "Enabled",
            "Filter": {"Prefix": ""},
            "Transitions": [
                {"Days": 30, "StorageClass": "STANDARD_IA"},
                {"Days": 90, "StorageClass": "GLACIER"}
            ],
            "Expiration": {"Days": 365},
            "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
        }
    ]
}
```

---

## 🤔 Concept 3 — What is S3 Bucket Policy?

```
Bucket Policy = JSON document controlling access to your bucket

Without policy:
→ Only your AWS account can access

With policy you can:
→ Allow specific IAM users to upload
→ Allow everyone to READ (public website)
→ Deny DELETE for everyone (protect data)
→ Allow only specific IP addresses
→ Require HTTPS for all access
```

**Policy structure:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "UniqueRuleName",
            "Effect": "Allow or Deny",
            "Principal": "WHO (user/role/* for everyone)",
            "Action": "WHAT (s3:GetObject, s3:PutObject etc)",
            "Resource": "WHICH (arn:aws:s3:::bucket/*)"
        }
    ]
}
```

**Critical rule:**
```
Effect: Deny ALWAYS wins over Effect: Allow
Even if another statement allows it — Deny wins
```

---

## 📋 AWS CLI Commands Practiced

### Versioning

```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# Check versioning status
aws s3api get-bucket-versioning \
  --bucket my-bucket

# List all versions of objects
aws s3api list-object-versions \
  --bucket my-bucket \
  --query 'Versions[*].[Key,VersionId,LastModified]' \
  --output table
```

### Lifecycle Policy

```bash
# Apply lifecycle policy from JSON file
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json

# Read current lifecycle policy
aws s3api get-bucket-lifecycle-configuration \
  --bucket my-bucket
```

---

## 🐍 Script 1 — s3_versioning.py

**What it does:**
```
Creates S3 bucket
Enables versioning
Uploads 3 versions of same file
Lists all versions with version IDs
Retrieves a specific old version (simulates rollback)
Cleans up everything
```

**Key functions explained:**

```python
# Enable versioning
s3.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={'Status': 'Enabled'}
)

# Upload — returns VersionId if versioning enabled
response = s3.put_object(
    Bucket=bucket_name,
    Key='config/app.json',
    Body=content.encode('utf-8')
)
version_id = response.get('VersionId')

# List all versions
response = s3.list_object_versions(
    Bucket=bucket_name,
    Prefix='config/app.json'  # filter to one file
)
versions = response.get('Versions', [])

# Get specific old version (RESTORE/ROLLBACK)
response = s3.get_object(
    Bucket=bucket_name,
    Key='config/app.json',
    VersionId='abc123def456'  # specific version ID
)

# Delete specific version permanently
s3.delete_object(
    Bucket=bucket_name,
    Key='config/app.json',
    VersionId='abc123def456'
)
```

**How to run:**
```bash
python3 s3_versioning.py
```

---

## 🐍 Script 2 — s3_lifecycle.py

**What it does:**
```
Creates S3 bucket
Uploads sample files (config, logs, reports, backups)
Applies 2-rule lifecycle policy
Verifies policy was applied
Calculates real cost savings
Cleans up
```

**Key lifecycle functions:**

```python
# Apply lifecycle policy
s3.put_bucket_lifecycle_configuration(
    Bucket=bucket_name,
    LifecycleConfiguration={
        'Rules': [
            {
                'ID': 'MainRule',
                'Status': 'Enabled',
                'Filter': {'Prefix': ''},  # applies to all objects
                'Transitions': [
                    {'Days': 30, 'StorageClass': 'STANDARD_IA'},
                    {'Days': 90, 'StorageClass': 'GLACIER'}
                ],
                'Expiration': {'Days': 365},
                'NoncurrentVersionExpiration': {'NoncurrentDays': 30}
            },
            {
                'ID': 'LogsRule',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'logs/'},  # only logs/ folder
                'Expiration': {'Days': 7}  # delete logs after 7 days
            }
        ]
    }
)

# Read current policy
response = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
rules = response['Rules']
```

**Cost savings formula:**
```python
hours_standard = 1 month    # $0.023/GB
hours_ia = 2 months         # $0.0125/GB
hours_glacier = 9 months    # $0.004/GB

cost_without = 100GB × $0.023 × 12 = $27.60
cost_with    = (100×0.023×1) + (100×0.0125×2) + (100×0.004×9)
             = $2.30 + $2.50 + $3.60 = $8.40
savings      = $27.60 - $8.40 = $19.20 (70% saved!)
```

**How to run:**
```bash
python3 s3_lifecycle.py
```

---

## 🐍 Script 3 — s3_bucket_policy.py

**What it does:**
```
Creates S3 bucket
Applies read-only + deny-delete policy
Reads back and displays the policy
Shows 3 common policy examples for learning
Cleans up
```

**Key policy functions:**

```python
# Build policy as Python dict
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAccountReadOnly",
            "Effect": "Allow",
            "Principal": {"AWS": f"arn:aws:iam::{account_id}:root"},
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*"
            ]
        },
        {
            "Sid": "DenyDelete",
            "Effect": "Deny",   # Deny wins over Allow always
            "Principal": "*",   # applies to everyone
            "Action": "s3:DeleteObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}

# Apply policy — must be JSON string not dict
s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)  # json.dumps() = dict to string
)

# Read policy back
response = s3.get_bucket_policy(Bucket=bucket_name)
policy = json.loads(response['Policy'])  # json.loads() = string to dict
```

**Common policy examples:**
```json
// 1. Public read (for static websites)
{"Effect": "Allow", "Principal": "*", "Action": "s3:GetObject"}

// 2. Deny non-HTTPS
{"Effect": "Deny", "Condition": {"Bool": {"aws:SecureTransport": "false"}}}

// 3. Allow specific user only
{"Principal": {"AWS": "arn:aws:iam::123456789:user/devops"}}
```

**How to run:**
```bash
python3 s3_bucket_policy.py
```

---

## 🧠 Key Lessons from Day 18

> **Lesson 1:** Always enable versioning on important buckets. Storage cost is small compared to the cost of lost data. One accidental delete without versioning = gone forever.

> **Lesson 2:** Lifecycle policies are free to set up and save significant money automatically. Every company with S3 data should have lifecycle policies — zero manual work after setup.

> **Lesson 3:** `Effect: Deny` always wins over `Effect: Allow` in bucket policies. Use Deny statements to protect critical data even from privileged users.

> **Lesson 4:** When deleting a versioned bucket — you must delete ALL versions AND delete markers first. Regular `delete_bucket()` fails if any versions exist.

> **Lesson 5:** `json.dumps()` converts Python dict to JSON string. `json.loads()` converts JSON string back to Python dict. S3 bucket policies must be passed as JSON strings not dicts.

---

## 🎯 Interview Questions

1. **What is S3 versioning and why would you enable it?**
   > S3 versioning keeps every version of every object uploaded to a bucket. Each upload creates a new version with a unique VersionId. You'd enable it to protect against accidental overwrites or deletes — you can restore any previous version instantly. Critical for config files, database backups, and any data where history matters.

2. **What is an S3 lifecycle policy?**
   > A lifecycle policy automatically moves objects between storage classes or deletes them based on age. For example: move to Standard-IA after 30 days (46% cheaper), move to Glacier after 90 days (83% cheaper), delete after 365 days. Runs automatically — no manual work needed after setup.

3. **What is the difference between S3 Standard, Standard-IA, and Glacier?**
   > Standard is for frequently accessed data — fast retrieval, highest cost ($0.023/GB). Standard-IA (Infrequent Access) is for data accessed monthly — same speed but lower storage cost with a retrieval fee ($0.0125/GB). Glacier is for archives — takes minutes to retrieve, very low storage cost ($0.004/GB). Use lifecycle policies to automatically move data between these tiers.

4. **How do you control access to an S3 bucket?**
   > Through bucket policies (JSON documents attached to the bucket) and IAM policies (attached to users/roles). Bucket policies can allow/deny specific actions for specific principals (users, roles, or everyone). Effect: Deny always wins over Effect: Allow regardless of other policies.

5. **How do you delete a versioned S3 bucket with boto3?**
   > You must first delete all object versions and delete markers before the bucket can be deleted. Use `list_object_versions()` to get all versions and markers, then `delete_objects()` with all their Keys and VersionIds, then finally `delete_bucket()`.

---

## 🔧 Troubleshooting

| Error | Why | Fix |
|-------|-----|-----|
| `BucketAlreadyExists` | Bucket name taken globally | Add unique suffix like timestamp |
| `NoSuchLifecycleConfiguration` | No lifecycle policy set | Apply one first with `put_bucket_lifecycle_configuration()` |
| `BucketNotEmpty` on delete | Bucket has objects/versions | Delete all versions and markers first |
| `MalformedPolicy` | Invalid JSON in bucket policy | Validate JSON at jsonlint.com |
| `InvalidArgument` on lifecycle | Transition days conflict | IA must be ≥30 days, Glacier must be after IA |
| `--query` error in CLI | Missing `--` before query | Use `--query` not `query` |

---

## 📁 Files in This Folder

```
Day-18/
├── README.md              ← This file
├── .env                   ← Config (not in GitHub)
├── .gitignore             ← Excludes .env and temp files
├── lifecycle.json         ← Lifecycle policy used with AWS CLI
├── test.txt               ← Sample file for versioning practice
├── s3_versioning.py       ← Versioning automation
├── s3_lifecycle.py        ← Lifecycle policy automation
└── s3_bucket_policy.py    ← Bucket policy automation
```

---

## ⬅️ Previous Day
[Day 17 — Advanced boto3: EC2 Automation](../Day-17/)

## ➡️ Next Day
[Day 19 — AWS IAM Deep Dive: Roles, Policies, Cross-Account](../Day-19/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*