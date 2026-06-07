# 📅 Day 16 — AWS CLI + boto3: Cloud Automation with Python

## 🎯 What is today about?

Today we stop clicking in AWS Console and start automating.

We learned two tools:
- **AWS CLI** — control AWS from your terminal
- **boto3** — control AWS from Python code

By the end of today we automated the full S3 lifecycle, checked EC2 infrastructure, and verified our AWS account health — all with Python scripts.

---

## 🏢 How real companies use these tools

| Tool | Real company use case |
|------|-----------------------|
| **AWS CLI** | DevOps engineers run CLI commands in shell scripts to automate deployments |
| **boto3** | Data engineers use boto3 to move files between S3 buckets automatically |
| **boto3** | DevOps teams write Python scripts to start/stop EC2 instances on schedule |
| **boto3** | Security teams scan IAM permissions across hundreds of accounts automatically |

---

## 🤔 What is AWS CLI?

**The problem without CLI:**
```
Create S3 bucket:
Open browser → login → click S3 →
click Create bucket → fill 5 fields → click Create
= 6 clicks, 2 minutes, cannot automate
```

**With AWS CLI:**
```bash
aws s3 mb s3://my-bucket
= 1 command, 2 seconds, fully automatable
```

**AWS CLI = control AWS from your terminal instead of browser**

Real engineers use CLI because:
- Faster than clicking
- Can be put in shell scripts
- Works inside CI/CD pipelines
- Can be version controlled

---

## 🤔 What is boto3?

AWS CLI is great for simple commands. But what if you need logic?

```
Problem: Delete all S3 buckets older than 30 days
AWS CLI: impossible — no loops, no conditions
boto3:   easy — Python loop + date comparison
```

**boto3 = AWS SDK for Python = control AWS from Python code**

```
AWS Console  → click in browser     (manual, slow)
AWS CLI      → type commands        (semi-automated)
boto3        → write Python code    (fully automated)
```

---

## 🤔 What is IAM? (Critical concept)

Before using AWS CLI you need credentials. These come from IAM.

```
IAM = Identity and Access Management

AWS account  = a company building
IAM user     = an employee with an ID card
IAM policy   = what doors the ID card opens
IAM role     = temporary ID card for AWS services
Access key   = password for CLI/boto3 access
```

### ⚠️ NEVER use root account for CLI

```
Root account   = master key — can do EVERYTHING
               = delete your entire AWS account
               = no restrictions at all

IAM user       = limited key — only what you allow
               = if compromised — limited damage
               = best practice always

Today we created:
IAM user: devops
Policies: S3FullAccess, EC2ReadOnly, IAMReadOnly
```

---

## 🤔 What is venv?

```
Without venv:
pip install boto3     → installed globally
pip install flask     → installed globally
Project A needs boto3 v1.0
Project B needs boto3 v2.0
They conflict → one breaks ❌

With venv:
Each project has its OWN Python environment
No conflicts → fully isolated ✅
```

### How to create and use venv

```bash
# Create virtual environment
python3 -m venv day16-venv

# Activate it
source day16-venv/bin/activate

# Prompt changes to show it's active
(day16-venv) harsha@HARSHA:~$

# Install packages inside venv
pip install boto3 python-dotenv

# Deactivate when done
deactivate
```

---

## 🤔 What is .env?

```
Problem: Your scripts need config like AWS region
Never hardcode these in your Python files
Never push credentials to GitHub

.env file = stores config variables separately
           = never committed to GitHub
           = loaded by python-dotenv library
```

### Our .env file

```
AWS_REGION=ap-south-1
S3_BUCKET_PREFIX=devops-journey-harsha
LOG_LEVEL=INFO
```

### How Python reads .env

```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file

REGION = os.getenv('AWS_REGION', 'ap-south-1')
```

### The complete security rule

```
~/.aws/credentials  → Access Key + Secret (set by aws configure)
.env                → App config (region, prefixes)
.gitignore          → Both excluded from git
GitHub Secrets      → For CI/CD pipelines
```

---

## 📋 Setup Done Today

### Step 1 — Install AWS CLI

```bash
# Check if installed
aws --version

# Install if missing
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Step 2 — Configure AWS CLI

```bash
aws configure
# AWS Access Key ID:     → your IAM user key
# AWS Secret Access Key: → your IAM user secret
# Default region:        → ap-south-1
# Default output format: → json

# Verify connection
aws sts get-caller-identity
```

### Step 3 — Create venv and install packages

```bash
python3 -m venv day16-venv
source day16-venv/bin/activate
pip install boto3 python-dotenv
pip freeze > requirements.txt
```

### Step 4 — Create .env and .gitignore

```bash
# .env
AWS_REGION=ap-south-1
S3_BUCKET_PREFIX=devops-journey-harsha
LOG_LEVEL=INFO

# .gitignore
.env
day16-venv/
__pycache__/
*.pyc
aws-health-*.json
```

---

## 🖥️ AWS CLI Commands Practiced

### S3 Commands

```bash
# List all buckets
aws s3 ls

# Create bucket
aws s3 mb s3://my-bucket --region ap-south-1

# Upload file
aws s3 cp local-file.txt s3://my-bucket/

# List files in bucket
aws s3 ls s3://my-bucket/

# Download file
aws s3 cp s3://my-bucket/file.txt local-file.txt

# Delete file
aws s3 rm s3://my-bucket/file.txt

# Delete bucket
aws s3 rb s3://my-bucket
```

### EC2 Commands

```bash
# List all instances
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]' \
  --output table

# List all VPCs
aws ec2 describe-vpcs \
  --query 'Vpcs[*].[VpcId,CidrBlock,IsDefault]' \
  --output table

# List security groups
aws ec2 describe-security-groups \
  --query 'SecurityGroups[*].[GroupId,GroupName]' \
  --output table
```

### IAM Commands

```bash
# See who you are
aws iam get-user

# List all users
aws iam list-users \
  --query 'Users[*].[UserName,CreateDate]' \
  --output table

# List all roles
aws iam list-roles \
  --query 'Roles[*].[RoleName,CreateDate]' \
  --output table
```

---

## 🐍 Python boto3 Scripts Built Today

### 1. aws_health_check.py

**What it does:**
```
Connects to AWS using boto3
Checks S3, EC2, IAM are all accessible
Shows bucket count, instance count, user count
Generates JSON health report saved to file
```

**How to run:**
```bash
python3 aws_health_check.py
```

**Output:**
```
🏥 AWS Health Check — Day 16 of 90
🔌 Checking AWS connection...
✅ Connected to AWS!
   Account ID : 750424847116
   User ARN   : arn:aws:iam::750424847116:user/devops
🪣 Checking S3...
✅ S3 accessible — 0 bucket(s) found
🖥️  Checking EC2 in ap-south-1...
✅ EC2 accessible — 0 instance(s) found
👤 Checking IAM...
✅ IAM accessible
   Users   : 1
   Roles   : 7
📋 Report saved: aws-health-2026-06-07.json
✅ Health check complete!
```

---

### 2. s3_manager.py

**What it does:**
```
Lists all existing S3 buckets
Creates a new bucket with unique timestamp name
Uploads a JSON file to the bucket
Lists files inside the bucket
Downloads the file back
Deletes everything — clean up
```

**How to run:**
```bash
python3 s3_manager.py
```

**Output:**
```
🪣 S3 Manager — Day 16 of 90
📦 Your S3 buckets (0 total):
Creating bucket: devops-journey-harsha-day16-20260607171455
✅ Bucket created
✅ Uploaded: day16-report.json
📁 Files: day16-report.json (151 bytes)
✅ Downloaded: day16-report.json
🧹 Cleaning up...
✅ Bucket deleted
✅ S3 Manager complete!
```

---

### 3. ec2_info.py

**What it does:**
```
Lists all EC2 instances with name, type, state
Lists all VPCs with CIDR blocks
Lists all security groups
One script to see your entire AWS compute infrastructure
```

**How to run:**
```bash
python3 ec2_info.py
```

**Output:**
```
🖥️  EC2 Info — Day 16 of 90
🖥️  EC2 Instances in ap-south-1: 0
   No instances found — none running yet
🌐 VPCs in ap-south-1:
   → vpc-0157c53179f5b81c5 | 172.31.0.0/16 | DEFAULT
🔒 Security Groups in ap-south-1:
   → sg-0e15c69f7b3fd8d14 | Devops-project
   → sg-05c0e807025afeda2 | default
✅ EC2 Info complete!
```

---

## 🧠 Key Lessons from Day 16

> **Lesson 1:** Never use root credentials for AWS CLI. Always create an IAM user with only the permissions needed. Root = master key. One leak = full account compromised.

> **Lesson 2:** Always use venv for Python projects. Isolates dependencies. Prevents version conflicts. Makes your setup reproducible for others.

> **Lesson 3:** Never hardcode credentials or config in Python files. Use `.env` for config and `~/.aws/credentials` for AWS keys. Never push either to GitHub.

> **Lesson 4:** boto3 follows the same pattern for every AWS service: `boto3.client('service')` → call method → get response. Learn the pattern once — works for all 200+ AWS services.

> **Lesson 5:** `requirements.txt` is your gift to other developers. Anyone can run `pip install -r requirements.txt` and get the exact same environment you used.

---

## 🎯 Interview Questions — Practice These

1. **What is the difference between AWS CLI and boto3?**
   > AWS CLI is a command-line tool for running individual AWS commands from the terminal — great for quick tasks and shell scripts. boto3 is the AWS SDK for Python — it lets you write Python code to automate complex AWS workflows with loops, conditions, and error handling. CLI is for humans typing commands, boto3 is for programs executing logic.

2. **Why should you never use root credentials for AWS CLI?**
   > Root credentials have unrestricted access to everything in your AWS account including billing, account deletion, and all services. If root credentials are leaked, an attacker has complete control. IAM users can be given minimal permissions needed for their task, limiting damage if credentials are compromised.

3. **What is IAM least privilege principle?**
   > Give users and services only the permissions they actually need — nothing more. A developer who only needs to read S3 should only have S3 read access, not EC2 or IAM admin. This limits the blast radius if credentials are compromised.

4. **How does boto3 authenticate with AWS?**
   > boto3 follows a credential chain: first checks environment variables, then `~/.aws/credentials` file (set by `aws configure`), then IAM instance profile if running on EC2. You never need to pass credentials directly in code — boto3 finds them automatically.

5. **What is a VPC and why does every AWS account have one?**
   > VPC (Virtual Private Cloud) is your own isolated private network inside AWS. Every AWS account gets a default VPC automatically so you can launch resources immediately. Custom VPCs give you full control over IP ranges, subnets, routing, and security — used in production for network isolation.

6. **What does `pip freeze > requirements.txt` do?**
   > It captures the exact version of every installed Python package in the current environment and saves it to requirements.txt. Anyone can then run `pip install -r requirements.txt` to install the exact same versions — ensuring consistent, reproducible environments across machines.

---

## ❓ Frequently Asked Questions

**Q: Where are AWS credentials stored locally?**
In `~/.aws/credentials` and `~/.aws/config` — created automatically by `aws configure`. Never in your code files.

**Q: What is ap-south-1?**
It's the AWS region code for Mumbai, India. Using the closest region gives lowest latency and often lower costs. Always use the region closest to your users or yourself for learning.

**Q: Can boto3 work without `aws configure`?**
Yes — boto3 also reads from environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) or IAM roles on EC2. But `aws configure` is the simplest approach for local development.

**Q: What is the difference between S3 object and S3 bucket?**
A bucket is the container — like a folder. An object is the file stored inside — like a document. Bucket names must be globally unique across all of AWS. You can have unlimited objects inside a bucket.

---

## 📁 Files in This Folder

```
Day-16/
├── README.md              ← This file
├── aws_health_check.py    ← Check AWS connection + all services
├── s3_manager.py          ← Full S3 lifecycle automation
├── ec2_info.py            ← EC2 infrastructure overview
├── requirements.txt       ← Python package versions
├── test-file.txt          ← Sample file used in CLI practice
├── download.txt           ← Downloaded from S3 during practice
└── .gitignore             ← Excludes .env and cache files
```

**Note:** `.env` is NOT in this folder on GitHub — it contains config and is excluded by `.gitignore`. Create your own `.env` using the template above.

---

## 🔧 Troubleshooting

| Error | Why | Fix |
|-------|-----|-----|
| `Unable to locate credentials` | AWS not configured | Run `aws configure` |
| `Access Denied` | IAM user missing permissions | Add required policy in IAM console |
| `BucketAlreadyExists` | Bucket name taken globally | Add unique suffix like timestamp |
| `InvalidClientTokenId` | Wrong access key | Re-run `aws configure` with correct keys |
| `dotenv not found` | python-dotenv not installed | `pip install python-dotenv` |
| Root credentials used | Created key from root account | Create IAM user, use that key instead |

---

## ⬅️ Previous Day
[Day 15 — GitHub Actions Advanced CI/CD](../Day-15/)

## ➡️ Next Day
[Day 17 — Advanced boto3: EC2 Automation](../Day-17/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
