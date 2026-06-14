# 📅 Day 17 — Advanced boto3: EC2 Automation

## 🎯 What is today about?

Yesterday we READ AWS resources.
Today we CONTROL them.

We built 3 Python scripts that automate EC2 instances — listing, starting, stopping, scheduling, and monitoring — all explained line by line for beginners.

---

## 🏢 How real companies use EC2 automation

| Use case | How boto3 helps |
|----------|----------------|
| **Cost saving** | Auto-stop dev instances at 7PM, auto-start at 9AM |
| **Health monitoring** | Check CPU every 5 minutes, alert if > 80% |
| **Multi-account management** | One script controls dev/staging/prod accounts |
| **Compliance reporting** | Generate daily report of all running instances |
| **Disaster recovery** | Auto-restart stopped instances if they crash |

---

## 🤔 Concept 1 — EC2 Instance Lifecycle

Every EC2 instance goes through these states:

```
pending → running → stopping → stopped
                              ↓
                          terminated (permanent delete)
```

```
pending    = starting up (takes 1-2 minutes)
running    = ON  — you pay per hour
stopping   = shutting down (takes 30-60 seconds)
stopped    = OFF — no compute charges (storage still costs)
terminated = DELETED — gone forever, cannot recover
```

**Key rules:**
```
stop()      → can restart later
terminate() → permanent, cannot undo
```

---

## 🤔 Concept 2 — Why EC2 Tags Are Critical

```
Tags = key-value labels on AWS resources

Example tags on an EC2 instance:
Name        = "web-server-01"
Environment = "production"
Owner       = "harsha"
Project     = "devops-journey"
```

**Without tags — dangerous automation:**
```python
# NEVER do this — stops ALL instances including production
ec2.stop_instances(InstanceIds=all_instance_ids)
```

**With tags — safe automation:**
```python
# Safe — only stops dev instances
response = ec2.describe_instances(
    Filters=[
        {'Name': 'tag:Environment', 'Values': ['dev']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
)
```

---

## 🤔 Concept 3 — Multi-Account AWS (STS AssumeRole)

Real companies have multiple AWS accounts:

```
Management account  → billing, governance
Dev account         → developer sandbox
Staging account     → pre-production testing
Production account  → real users
```

**How AssumeRole works:**
```
Step 1: Your account calls sts.assume_role(role_arn)
Step 2: STS checks if you're allowed to assume that role
Step 3: STS returns temporary credentials (valid 1 hour)
Step 4: Use credentials to create a new boto3 session
Step 5: That session controls the target account
```

**Code example:**
```python
sts = boto3.client('sts')
response = sts.assume_role(
    RoleArn='arn:aws:iam::111122223333:role/DevOpsRole',
    RoleSessionName='AutomationSession'
)
credentials = response['Credentials']
session = boto3.Session(
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']  # required for temp creds
)
ec2 = session.client('ec2')  # now controls the target account
```

---

## 🤔 Concept 4 — CloudWatch Metrics

```
CloudWatch = AWS monitoring service
Automatically collects metrics for all AWS resources

EC2 metrics available:
CPUUtilization    (%)
NetworkIn/Out     (bytes)
DiskReadOps       (count)
StatusCheckFailed (0 or 1)
```

---

## 📁 Project Structure

```
Day-17/
├── README.md              ← This file
├── .env                   ← Config (not in GitHub)
├── .gitignore             ← Excludes .env and cache
├── requirements.txt       ← Python packages
├── ec2_controller.py      ← List, start, stop EC2
├── ec2_scheduler.py       ← Time-based automation
└── ec2_monitor.py         ← CloudWatch monitoring
```

---

## ⚙️ Setup

```bash
# 1. Activate virtual environment
source devops-venv/bin/activate

# 2. Install packages
pip install boto3 python-dotenv

# 3. Create .env file
nano .env
```

**.env contents:**
```
AWS_REGION=ap-south-1
EC2_TAG_KEY=Environment
EC2_TAG_VALUE=dev
MANAGEMENT_ACCOUNT=your-account-id
ASSUME_ROLE_NAME=DevOpsAutomationRole
```

---

## 🐍 Script 1 — ec2_controller.py

**What it does:**
```
Lists all EC2 instances in your account
Filters instances by tag (Environment=dev)
Can stop running instances safely
Can start stopped instances
Generates JSON report
Supports multi-account via AssumeRole
```

**Key functions:**
```python
# List all instances
ec2.describe_instances()

# Filter by tag
ec2.describe_instances(
    Filters=[{'Name': 'tag:Environment', 'Values': ['dev']}]
)

# Stop instances
ec2.stop_instances(InstanceIds=['i-1234567890abcdef0'])

# Start instances
ec2.start_instances(InstanceIds=['i-1234567890abcdef0'])
```

**How to run:**
```bash
python3 ec2_controller.py
```

---

## 🐍 Script 2 — ec2_scheduler.py

**What it does:**
```
Checks current time automatically
Work hours (9AM-7PM) → starts stopped dev instances
After hours (7PM-9AM) → stops running dev instances
Calculates and shows monthly cost savings
```

**Cost savings proved today:**
```
5 instances example:
Without scheduler : $360.00/month
With scheduler    : $110.00/month
Monthly savings   : $250.00 (69% saved!)
Zero manual work
```

**How to run:**
```bash
python3 ec2_scheduler.py
```

---

## 🐍 Script 3 — ec2_monitor.py

**What it does:**
```
Gets all non-terminated instances
For running instances → pulls CPU from CloudWatch
Flags instances with CPU > 80% as WARNING
Saves monitoring report to JSON file
```

**CloudWatch call explained:**
```python
cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',         # EC2 metrics namespace
    MetricName='CPUUtilization', # which metric
    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
    StartTime=datetime.utcnow() - timedelta(hours=1), # last hour
    EndTime=datetime.utcnow(),
    Period=300,                  # 5-minute chunks
    Statistics=['Average']       # average CPU per chunk
)
```

**How to run:**
```bash
python3 ec2_monitor.py
```

---

## 🧠 Key Lessons from Day 17

> **Lesson 1:** Always filter EC2 automation by tags. Never run start/stop on ALL instances. One wrong script can take down your entire production environment.

> **Lesson 2:** STS AssumeRole is how companies manage multiple AWS accounts from one script. Temporary credentials are valid for 1 hour and require a SessionToken.

> **Lesson 3:** SessionToken is REQUIRED for temporary credentials from AssumeRole. Regular IAM user credentials don't need it.

> **Lesson 4:** CloudWatch stores metrics only for RUNNING instances. Stopped instances have no CPU metrics. Data appears after ~5 minutes of running.

> **Lesson 5:** The EC2 scheduler is one of the most common boto3 automations in real companies. Dev instances running 24/7 = wasted money.

---

## 🎯 Interview Questions

1. **How do you safely automate EC2 instances without affecting production?**
   > Use tag-based filtering. Tag dev instances with `Environment=dev` and production with `Environment=prod`. Write scripts that filter by tag before any action. Never run automation against all instances without a tag filter.

2. **What is STS AssumeRole and when would you use it?**
   > STS AssumeRole lets your account get temporary credentials to access another AWS account. Used for multi-account management — one script controls dev, staging, and production accounts. Temporary credentials are valid for 1 hour and require a SessionToken.

3. **What is the difference between stop and terminate for EC2?**
   > Stop shuts down the instance but keeps it — you can restart later and data is preserved. Terminate permanently deletes the instance — cannot be recovered. Always stop instances you might need again.

4. **What is CloudWatch and how do you get EC2 metrics with boto3?**
   > CloudWatch is AWS's monitoring service that automatically collects metrics. Use `cloudwatch.get_metric_statistics()` with namespace `AWS/EC2`, metric name `CPUUtilization`, and dimension `InstanceId` to get CPU for a specific instance.

5. **How would you build a cost-saving EC2 scheduler?**
   > Filter instances by `Environment=dev` tag. Check current time and start/stop accordingly. Running dev instances only during work hours (10hrs/day vs 24hrs) saves ~69% on compute costs.

---

## 🔧 Troubleshooting

| Error | Why | Fix |
|-------|-----|-----|
| `NoCredentialsError` | AWS not configured | Run `aws configure` |
| `AccessDenied` on stop | IAM missing EC2 permission | Add `AmazonEC2FullAccess` policy |
| `AccessDenied` on AssumeRole | Trust policy not set up | Add trust policy in target account |
| Management account shows `None` | Typo in .env | Check: `MANAGEMENT_ACCOUNT` not `MANGEMENT_ACCOUNT` |
| CloudWatch returns no data | Instance just started | Wait 5 minutes for metrics |

---

## ⬅️ Previous Day
[Day 16 — AWS CLI + boto3 Fundamentals](../Day-16/)

## ➡️ Next Day
[Day 18 — AWS S3 Advanced: Versioning, Lifecycle, Replication](../Day-18/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
