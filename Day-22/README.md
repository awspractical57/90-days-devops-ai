# Day 22 - AWS CloudWatch: Monitoring, Alarms & Dashboards

## What I learned today

CloudWatch = AWS monitoring and observability service.
Every AWS service sends metrics to CloudWatch automatically.
You set alarms on those metrics and get notified when something goes wrong.

---

## Concepts covered

### Core components

```
Metrics    = numbers over time (CPU%, error count, request duration)
Alarms     = rules that watch a metric and trigger action at threshold
Logs       = text output from services (Lambda logs, VPC flow logs)
Dashboards = visual view combining multiple metrics in one place
Events     = respond to AWS resource state changes automatically
```

### Namespaces

```
AWS/EC2     = CPUUtilization, NetworkIn, NetworkOut, DiskReadOps
AWS/Lambda  = Invocations, Errors, Duration, Throttles
AWS/S3      = BucketSizeBytes, NumberOfObjects, AllRequests
AWS/RDS     = CPUUtilization, DatabaseConnections, FreeStorageSpace
Custom      = your own application metrics (DevOpsJourney/Application)
```

### Alarm states

```
OK                = metric is within threshold - all good
ALARM             = metric crossed threshold - action triggered
INSUFFICIENT_DATA = not enough data to evaluate yet (new alarm)
```

INSUFFICIENT_DATA is normal for a new alarm.
It changes to OK or ALARM once metric data arrives.

### SNS for notifications

```
SNS Topic      = channel that receives alarm notifications
Subscription   = who gets notified (email, SMS, Lambda, SQS, HTTP)
Workflow:
  Alarm fires -> publishes to SNS topic -> SNS emails all subscribers
```

---

## AWS CLI hands-on

```bash
# list EC2 metrics available
aws cloudwatch list-metrics \
  --namespace AWS/EC2 \
  --query 'Metrics[*].[MetricName]' \
  --output table

# get CPU metric for last 1 hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average \
  --output table

# create SNS topic
aws sns create-topic --name devops-journey-alerts

# subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-south-1:750424847116:devops-journey-alerts \
  --protocol email \
  --notification-endpoint valajaharshatheja@gmail.com

# create CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name devops-journey-high-cpu \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:ap-south-1:750424847116:devops-journey-alerts

# list alarms
aws cloudwatch describe-alarms \
  --query 'MetricAlarms[*].[AlarmName,StateValue,Threshold]' \
  --output table

# cleanup
aws cloudwatch delete-alarms --alarm-names devops-journey-high-cpu
aws sns delete-topic --topic-arn arn:aws:sns:ap-south-1:750424847116:devops-journey-alerts
```

---

## Script: cloudwatch_monitor.py

**What it does:**
1. Creates SNS topic + subscribes email for notifications
2. Fetches EC2 CPUUtilization metrics for last 1 hour
3. Fetches Lambda metrics (invocations, errors, duration)
4. Creates CPU alarm (fires if CPU > 80% for 10 minutes)
5. Creates Lambda error alarm (fires if errors > 5 in 5 minutes)
6. Lists all alarms with current state
7. Publishes custom application metrics
8. Saves monitoring report as JSON
9. Cleans up all resources

**Key functions:**

| Function | Purpose |
|---|---|
| `create_sns_topic()` | Creates SNS topic + subscribes email |
| `get_ec2_metrics()` | Fetches CPUUtilization datapoints |
| `get_lambda_metrics()` | Fetches invocations, errors, duration |
| `create_cpu_alarm()` | Creates EC2 CPU threshold alarm |
| `create_lambda_error_alarm()` | Creates Lambda error count alarm |
| `list_alarms()` | Lists all alarms with state |
| `put_custom_metric()` | Publishes custom app metric |
| `generate_report()` | Saves JSON monitoring report |
| `cleanup()` | Deletes alarms and SNS topic |

---

## Script output

```
CloudWatch Monitor - Day 22 of 90
==================================================
SNS topic created: arn:aws:sns:ap-south-1:750424847116:devops-journey-alerts
Email subscribed: valajaharshatheja@gmail.com
  Check your email to confirm subscription!

EC2 CPUUtilization (last 1h): 0 datapoints
  No data - no EC2 instances running

Lambda Metrics (last 1h):
  Invocations : 0
  Errors      : 0
  Duration    : 0ms total

Creating alarms...
CPU alarm created: devops-journey-high-cpu (threshold: 80%)
Lambda error alarm created: devops-journey-lambda-errors (threshold: 5 errors)

CloudWatch Alarms: 2
==================================================
  [NO DATA] devops-journey-high-cpu
    Metric    : CPUUtilization
    Threshold : GreaterThanThreshold 80.0
    State     : INSUFFICIENT_DATA
  [NO DATA] devops-journey-lambda-errors
    Metric    : Errors
    Threshold : GreaterThanThreshold 5.0
    State     : INSUFFICIENT_DATA

Publishing custom metric...
Custom metric published: DeploymentCount = 1 Count
Custom metric published: HealthScore = 100 Count

Report saved: cloudwatch-report-2026-11-04.json

Cleaning up...
Alarms deleted: ['devops-journey-high-cpu', 'devops-journey-lambda-errors']
SNS topic deleted

CloudWatch Monitor complete!
```

---

## Key rules

- INSUFFICIENT_DATA is normal for new alarms - not an error
- EvaluationPeriods=2 prevents false alarms from brief CPU spikes
- TreatMissingData=notBreaching avoids alarms when instances are stopped
- Never use AWS/* as custom metric namespace - reserved for AWS services
- Always confirm SNS email subscription before alarms can notify you
- Custom metrics cost $0.30/metric/month after free tier

---

## Alarm design best practices

```
CPU alarm:
- Threshold  : 80% (not 100% - leave headroom)
- Periods    : 2 x 5min = alert only if sustained for 10 minutes
- Why        : brief spikes are normal, sustained high CPU is a problem

Lambda error alarm:
- Threshold  : 5 errors per 5 minutes
- Periods    : 1 (alert immediately on errors)
- Why        : errors should never happen in bursts

Missing data:
- notBreaching = stopped instances don't trigger alarms
- breaching    = use for critical services that must always run
```

---

## Custom metrics use cases

```
DeploymentCount  = track how many deployments happened today
HealthScore      = application health as a number (0-100)
ActiveUsers      = current users in your application
QueueDepth       = messages waiting to be processed
ErrorRate        = percentage of failed requests
```

---

## Files

```
Day-22/
├── cloudwatch_monitor.py    - full CloudWatch automation with boto3
├── .env                     - AWS_REGION, ALARM_EMAIL, ALARM_PREFIX
├── .gitignore               - excludes .env, *.pyc, report JSON files
└── README.md                - this file
```

---

## Progress

| Day | Topic | Status |
|-----|-------|--------|
| 19 | IAM deep dive | Done |
| 20 | VPC deep dive | Done |
| 21 | Lambda serverless | Done |
| 22 | CloudWatch monitoring | Done |
| 23 | AWS Cost Optimization | Next |

---

GitHub: [github.com/awspractical57/90-days-devops-ai](https://github.com/awspractical57/90-days-devops-ai)
