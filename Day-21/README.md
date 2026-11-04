# Day 21 - AWS Lambda: Serverless Automation

## What I learned today

Lambda = run code without managing any servers.
You write the function, AWS handles everything else - servers, scaling, patching, availability.

Traditional server vs Lambda:
- Server: running 24/7, you pay even when idle, you manage OS and patches
- Lambda: runs only when triggered, you pay per 100ms of execution, zero server management

---

## Concepts covered

### Lambda basics

```
Function  = your code packaged as zip
Runtime   = language and version (python3.11, nodejs18.x, java11 etc)
Handler   = entry point - format is filename.function_name
Trigger   = what starts the function (S3, API Gateway, CloudWatch Events, SNS etc)
Event     = input data passed to your function when triggered
Context   = AWS runtime info (remaining time, memory, request ID)
```

### Handler format explained

```
health_checker.lambda_handler means:
  - File:     health_checker.py
  - Function: lambda_handler inside that file

def lambda_handler(event, context):
    # event   = what triggered this (S3 key, HTTP request, scheduled event etc)
    # context = AWS runtime info
    return {"statusCode": 200, "body": "response"}
```

### Lambda states

```
Pending = being created, NOT ready to invoke
Active  = ready to invoke
Failed  = creation failed

Always wait for Active state before invoking.
Use waiter('function_active') in boto3.
```

### IAM role for Lambda

Lambda needs an IAM role to:
- Write logs to CloudWatch (AWSLambdaBasicExecutionRole)
- Access other AWS services (S3, DynamoDB, EC2 etc - add policies as needed)

Trust policy says who can assume the role:
```json
{
  "Principal": {"Service": "lambda.amazonaws.com"},
  "Action": "sts:AssumeRole"
}
```

### Cost comparison

```
EC2 t3.micro (24/7):   $8.47/month
Lambda (1M requests):  $0.20/month

For event-driven workloads = Lambda wins on cost.
For long-running processes = EC2 is better.
```

---

## AWS CLI hands-on

### Create IAM role for Lambda

```bash
aws iam create-role \
  --role-name DevOpsLambdaRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name DevOpsLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Package and deploy function

```bash
# package code as zip
zip health_checker.zip health_checker.py

# get role ARN
ROLE_ARN=$(aws iam get-role --role-name DevOpsLambdaRole --query 'Role.Arn' --output text)

# create function
aws lambda create-function \
  --function-name devops-health-checker \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler health_checker.lambda_handler \
  --zip-file fileb://health_checker.zip
```

### Invoke function

```bash
aws lambda invoke \
  --function-name devops-health-checker \
  --payload '{"source": "manual-test"}' \
  --cli-binary-format raw-in-base64-out \
  output.json

cat output.json
```

### List and delete

```bash
# list all functions
aws lambda list-functions \
  --query 'Functions[*].[FunctionName,Runtime,LastModified]' \
  --output table

# delete function
aws lambda delete-function --function-name devops-health-checker
```

---

## Script: lambda_manager.py

Full Lambda lifecycle automated with boto3.

**What it does:**
1. Creates IAM role with Lambda trust policy
2. Waits 15 seconds for role to propagate across AWS
3. Packages Python function code as zip
4. Creates Lambda function (python3.11, 128MB, 30s timeout)
5. Waits for function to reach Active state
6. Invokes function with test payload
7. Lists all Lambda functions in account
8. Cleans up all resources

**Key functions:**

| Function | Purpose |
|---|---|
| `create_lambda_role()` | Creates IAM role + attaches execution policy |
| `create_zip_package()` | Packages Python code as zip for deployment |
| `create_lambda_function()` | Creates function + waits for Active state |
| `invoke_lambda()` | Invokes function + returns response |
| `update_lambda_code()` | Updates existing function with new code |
| `list_functions()` | Lists all Lambda functions in region |
| `cleanup()` | Deletes function, role, local zip files |

---

## Script output

```
Lambda Manager - Day 21 of 90
==================================================
Role created: arn:aws:iam::750424847116:role/DevOpsLambdaRole
Basic execution policy attached
Waiting 15 seconds for role to propagate...
Zip package created: health_checker.zip
Function created: devops-health-checker
  Runtime : python3.11
  Memory  : 128MB
  Timeout : 30s
  Status  : Active (ready to invoke)

Invoking function...

Function invoked successfully!
  Status code : 200
  Response    : {
    "statusCode": 200,
    "body": "{\"message\": \"Health check passed\", \"day\": \"Day 21 of 90\"}"
  }

Lambda Functions in ap-south-1: 1
  Name    : devops-health-checker
  Runtime : python3.11
  Memory  : 128MB

Cleaning up...
Function deleted: devops-health-checker
Role deleted: DevOpsLambdaRole
Local files cleaned up

Lambda Manager complete!
```

---

## Bugs fixed today

**Bug 1 - ResourceConflictException on invoke:**
```
Error: function is currently in the following state: Pending
Fix:  add waiter('function_active') after create_function()
      waiter polls every 5 seconds until state = Active
```

**Bug 2 - InvalidParameterValueException on create:**
```
Error: role cannot be assumed (immediately after create_role)
Fix:  add time.sleep(15) after role creation
      AWS takes 10-15 seconds to propagate IAM role across regions
```

---

## Key rules

- Always wait for Active state before invoking - use `get_waiter('function_active')`
- Always sleep 10-15 seconds after creating IAM role before using it in Lambda
- Handler format is `filename.function_name` - no .py extension
- Zip must contain .py file at root level - not inside a subfolder
- Trust policy and execution policy are both required - one is not enough
- Never hardcode AWS account ID - use environment variables or STS get_caller_identity()

---

## Lambda limits to know

```
Max timeout:        15 minutes (900 seconds)
Max memory:         10 GB
Max zip size:       50 MB (direct), 250 MB (from S3)
Max /tmp storage:   10 GB
Cold start:         first invocation takes longer (container spin-up)
Free tier:          1M requests/month, 400,000 GB-seconds/month
```

---

## Real-world use cases

```
S3 trigger:        file uploaded -> Lambda resizes image automatically
CloudWatch Events: 9AM every day -> Lambda starts dev EC2 instances
API Gateway:       HTTP POST -> Lambda processes request -> returns response
SNS trigger:       alert fires -> Lambda sends Slack notification
```

---

## Files

```
Day-21/
├── lambda_manager.py   - full Lambda lifecycle with boto3
├── .env                - AWS_REGION, LAMBDA_ROLE_NAME, LAMBDA_FUNCTION_NAME
├── .gitignore          - excludes .env, __pycache__, *.zip
└── README.md           - this file
```

---

## Progress

| Day | Topic | Status |
|-----|-------|--------|
| 16 | AWS CLI + boto3 basics | Done |
| 17 | EC2 automation | Done |
| 18 | S3 advanced | Done |
| 19 | IAM deep dive | Done |
| 20 | VPC deep dive | Done |
| 21 | Lambda serverless | Done |
| 22 | CloudWatch monitoring | Next |

---

GitHub: [github.com/awspractical57/90-days-devops-ai](https://github.com/awspractical57/90-days-devops-ai)
