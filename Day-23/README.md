# Day 23 - AWS Cost Optimization

## What I learned today

Cloud cost waste is real. Average company wastes 32% of cloud spend.
The fix is visibility first - you cannot optimize what you cannot see.
CloudWatch shows performance. Cost Explorer shows money.

---

## Concepts covered

### Core tools

```
Cost Explorer     = visual breakdown of AWS spend by service, region, tag
Budgets           = set monthly limits, get alerted before overspending
Cost Allocation Tags = tag resources to track cost by project/team/env
Trusted Advisor   = AWS recommendations for cost, security, performance
Rightsizing       = match instance size to actual usage
```

### Common cost waste patterns

```
Stopped EC2        = instance stopped but EBS volume still charges ($0.08/GB/month)
Unattached EBS     = volume exists but nothing is using it
Unattached EIP     = Elastic IP not assigned to running instance ($3.60/month each)
Old snapshots      = accumulate silently, easy to forget
Over-provisioned   = t3.xlarge running at 5% CPU - should be t3.micro
Data transfer OUT  = charges money - data transfer IN is free
```

### Budget alert types

```
ACTUAL      = alert when real spend crosses threshold (80% of $10 = alert at $8)
FORECASTED  = alert when projected spend will exceed budget (early warning)

Both together = best protection against surprise bills
```

---

## AWS CLI hands-on

```bash
# get current month cost by service
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[*].[Keys[0],Metrics.BlendedCost.Amount]' \
  --output table

# get total cost this month
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text

# create monthly budget with email alert
aws budgets create-budget \
  --account-id 750424847116 \
  --budget '{
    "BudgetName": "devops-journey-monthly",
    "BudgetLimit": {"Amount": "10", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "valajaharshatheja@gmail.com"
    }]
  }]'

# list budgets
aws budgets describe-budgets \
  --account-id 750424847116 \
  --query 'Budgets[*].[BudgetName,BudgetLimit.Amount,BudgetType]' \
  --output table

# delete budget
aws budgets delete-budget \
  --account-id 750424847116 \
  --budget-name devops-journey-monthly
```

---

## Script: cost_optimizer.py

**What it does:**
1. Gets current month cost breakdown by AWS service
2. Shows monthly cost trend for last 3 months
3. Creates monthly budget with 80% actual + 100% forecasted alerts
4. Lists all budgets with current spend vs limit
5. Scans for cost waste - stopped EC2, unattached EBS, unattached EIPs
6. Saves cost optimization report as JSON
7. Cleans up budget

**Key functions:**

| Function | Purpose |
|---|---|
| `get_cost_by_service()` | Breaks down spend by AWS service this month |
| `get_cost_trend()` | Shows monthly spend for last N months |
| `create_budget()` | Creates budget with dual email alerts |
| `list_budgets()` | Lists all budgets with spend percentage |
| `analyze_cost_savings()` | Finds stopped EC2, unattached EBS and EIPs |
| `generate_report()` | Saves JSON cost report |
| `cleanup()` | Deletes budget created in session |

**Important:** Cost Explorer client must use `us-east-1` - it is a global service regardless of your working region.

---

## Script output

```
Cost Optimizer - Day 23 of 90
==================================================
Cost by Service (this month): $0.0001 USD
  Amazon Simple Storage Service    $0.0001  ####################

Monthly Cost Trend (last 3 months):
  2026-09  $0.0001
  2026-10  $0.0001
  2026-11  $0.0001

Budget created: devops-journey-monthly
  Limit     : $10.0/month
  Alert at  : 80% actual + 100% forecasted
  Email     : valajaharshatheja@gmail.com

Budgets: 1
  devops-journey-monthly
    Limit  : $10.00/month
    Spent  : $0.0000 (0.0%)
    Type   : COST

Cost Savings Analysis:
  No waste detected - resources look clean!

Report saved: cost-report-2026-11-04.json

Cleaning up...
Budget deleted: devops-journey-monthly

Cost Optimizer complete!
```

---

## Key rules

- Cost Explorer client region must always be `us-east-1` - it is global
- Budgets client region must always be `us-east-1` - same reason
- End date in Cost Explorer is EXCLUSIVE - use today's date, not tomorrow
- Always set both ACTUAL and FORECASTED budget alerts - two layers of protection
- Tag every resource from day one - untagged resources = invisible cost
- Stopped EC2 still charges for EBS - terminate instead of stop if not needed
- Unattached Elastic IPs cost $3.60/month each - release immediately when done

---

## Real-world cost optimization checklist

```
Weekly:
- Review Cost Explorer for unexpected spikes
- Check for unattached EBS volumes and EIPs
- Verify no test instances left running

Monthly:
- Review budget vs actual
- Check for over-provisioned instances (CPU < 10% = downsize)
- Delete old snapshots (keep only last 2-3)
- Review data transfer costs

One-time setup:
- Enable Cost Allocation Tags on all resources
- Set budget alerts at 50%, 80%, 100%
- Enable AWS Cost Anomaly Detection
```

---

## Files

```
Day-23/
├── cost_optimizer.py      - cost analysis and budget automation with boto3
├── .env                   - AWS_REGION, BUDGET_NAME, BUDGET_LIMIT, ALERT_EMAIL
├── .gitignore             - excludes .env, *.pyc, cost-report JSON files
└── README.md              - this file
```

---

## Progress

| Day | Topic | Status |
|-----|-------|--------|
| 20 | VPC deep dive | Done |
| 21 | Lambda serverless | Done |
| 22 | CloudWatch monitoring | Done |
| 23 | Cost optimization | Done |
| 24 | Terraform basics | Next |

---

GitHub: [github.com/awspractical57/90-days-devops-ai](https://github.com/awspractical57/90-days-devops-ai)
