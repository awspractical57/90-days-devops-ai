import boto3
import os
import json
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '750424847116')
BUDGET_NAME = os.getenv('BUDGET_NAME', 'devops-journey-monthly')
BUDGET_LIMIT = float(os.getenv('BUDGET_LIMIT', '10'))
ALERT_EMAIL = os.getenv('ALERT_EMAIL')


def get_ce_client():
    # Cost Explorer is a global service - always us-east-1
    return boto3.client('ce', region_name='us-east-1')


def get_budgets_client():
    # Budgets is a global service - always us-east-1
    return boto3.client('budgets', region_name='us-east-1')


def get_cost_by_service(days=30):
    """
    Get AWS cost breakdown by service for last N days.

    Cost Explorer API notes:
    - client region must be us-east-1 (global service)
    - End date is EXCLUSIVE (use tomorrow's date for today)
    - BlendedCost = average cost across all reserved and on-demand
    - UnblendedCost = actual cost per account (better for single account)
    - AmortizedCost = spreads reservation cost over usage period

    GROUP BY SERVICE breaks total cost by each AWS service.
    """
    ce = get_ce_client()

    # time period: start of current month to today
    start = date.today().replace(day=1).isoformat()
    # end date is exclusive in Cost Explorer - use today
    end = date.today().isoformat()

    # handle case where start == end (first day of month)
    if start == end:
        from datetime import timedelta
        end = (date.today() + timedelta(days=1)).isoformat()

    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    services = []
    total = 0.0

    for group in response['ResultsByTime'][0]['Groups']:
        service = group['Keys'][0]
        amount = float(group['Metrics']['BlendedCost']['Amount'])
        if amount > 0:
            services.append({'service': service, 'cost': amount})
            total += amount

    # sort by cost descending
    services.sort(key=lambda x: x['cost'], reverse=True)

    print(f"\nCost by Service (this month): ${total:.4f} USD")
    print("=" * 50)
    for s in services:
        # bar chart in terminal
        bar = '#' * int(s['cost'] / total * 20) if total > 0 else ''
        print(f"  {s['service'][:35]:<35} ${s['cost']:.4f}  {bar}")

    return services, total


def get_cost_trend(months=3):
    """
    Get monthly cost trend for last N months.

    Shows whether spending is increasing, stable or decreasing.
    Useful for identifying cost anomalies.
    """
    ce = get_ce_client()

    from datetime import timedelta
    end = date.today().isoformat()
    # go back N months from start of current month
    start_month = date.today().replace(day=1)
    for _ in range(months - 1):
        # go back one month
        start_month = (start_month - timedelta(days=1)).replace(day=1)
    start = start_month.isoformat()

    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['BlendedCost']
    )

    print(f"\nMonthly Cost Trend (last {months} months):")
    print("=" * 50)
    for period in response['ResultsByTime']:
        month = period['TimePeriod']['Start'][:7]
        amount = float(period['Total']['BlendedCost']['Amount'])
        bar = '#' * int(amount * 10) if amount > 0 else '-'
        print(f"  {month}  ${amount:.4f}  {bar}")

    return response['ResultsByTime']


def create_budget(budget_name, limit_usd, alert_threshold_pct=80):
    """
    Create monthly budget with email alert.

    Budget types:
    - COST    = dollar amount spending limit
    - USAGE   = service usage units (API calls, GB stored etc)
    - RI_UTILIZATION = ensure reserved instances are being used

    Notification types:
    - ACTUAL    = alert when actual spend crosses threshold
    - FORECASTED = alert when projected spend will cross threshold

    ThresholdType:
    - PERCENTAGE = threshold is % of budget (80 = alert at 80% spent)
    - ABSOLUTE_VALUE = threshold is dollar amount
    """
    budgets = get_budgets_client()

    budget = {
        'BudgetName': budget_name,
        'BudgetLimit': {
            'Amount': str(limit_usd),
            'Unit': 'USD'
        },
        'TimeUnit': 'MONTHLY',
        'BudgetType': 'COST'
    }

    notifications = [{
        'Notification': {
            'NotificationType': 'ACTUAL',
            'ComparisonOperator': 'GREATER_THAN',
            'Threshold': alert_threshold_pct,
            'ThresholdType': 'PERCENTAGE'
        },
        'Subscribers': [{
            'SubscriptionType': 'EMAIL',
            'Address': ALERT_EMAIL
        }]
    }, {
        # second alert at 100% using forecasted spend
        'Notification': {
            'NotificationType': 'FORECASTED',
            'ComparisonOperator': 'GREATER_THAN',
            'Threshold': 100,
            'ThresholdType': 'PERCENTAGE'
        },
        'Subscribers': [{
            'SubscriptionType': 'EMAIL',
            'Address': ALERT_EMAIL
        }]
    }]

    try:
        budgets.create_budget(
            AccountId=ACCOUNT_ID,
            Budget=budget,
            NotificationsWithSubscribers=notifications
        )
        print(f"\nBudget created: {budget_name}")
        print(f"  Limit     : ${limit_usd}/month")
        print(f"  Alert at  : {alert_threshold_pct}% actual + 100% forecasted")
        print(f"  Email     : {ALERT_EMAIL}")
    except Exception as e:
        if 'DuplicateRecordException' in str(e):
            print(f"Budget already exists: {budget_name}")
        else:
            print(f"Error creating budget: {e}")


def list_budgets():
    """List all budgets with current spend vs limit."""
    budgets = get_budgets_client()

    response = budgets.describe_budgets(AccountId=ACCOUNT_ID)
    budget_list = response.get('Budgets', [])

    print(f"\nBudgets: {len(budget_list)}")
    print("=" * 50)
    for b in budget_list:
        limit = float(b['BudgetLimit']['Amount'])
        # actual spend may not exist for new budgets
        actual = float(
            b.get('CalculatedSpend', {})
             .get('ActualSpend', {})
             .get('Amount', 0)
        )
        pct = (actual / limit * 100) if limit > 0 else 0
        print(f"  {b['BudgetName']}")
        print(f"    Limit  : ${limit:.2f}/month")
        print(f"    Spent  : ${actual:.4f} ({pct:.1f}%)")
        print(f"    Type   : {b['BudgetType']}")

    return budget_list


def analyze_cost_savings():
    """
    Analyze potential cost savings based on current resources.

    Checks:
    - Stopped EC2 instances still paying for EBS
    - Unattached EBS volumes (paying for storage, using nothing)
    - Old snapshots (accumulate over time, easy to forget)
    - Elastic IPs not attached to running instance ($0.005/hr = $3.6/month each)
    """
    ec2 = boto3.client('ec2', region_name=REGION)

    savings = []
    total_monthly_waste = 0.0

    # check for stopped instances (still paying for EBS)
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
    )
    stopped = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            stopped.append(instance['InstanceId'])

    if stopped:
        # EBS gp3 costs $0.08/GB/month, default root volume = 8GB = $0.64/month
        estimated_ebs_cost = len(stopped) * 0.64
        total_monthly_waste += estimated_ebs_cost
        savings.append({
            'issue': 'Stopped EC2 instances',
            'count': len(stopped),
            'instances': stopped,
            'monthly_waste': estimated_ebs_cost,
            'action': 'Terminate if not needed, or create AMI and terminate'
        })

    # check for unattached EBS volumes
    response = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    unattached = response['Volumes']
    if unattached:
        # gp3 = $0.08/GB/month
        total_gb = sum(v['Size'] for v in unattached)
        estimated_cost = total_gb * 0.08
        total_monthly_waste += estimated_cost
        savings.append({
            'issue': 'Unattached EBS volumes',
            'count': len(unattached),
            'total_gb': total_gb,
            'monthly_waste': estimated_cost,
            'action': 'Delete if no longer needed'
        })

    # check for unattached Elastic IPs
    response = ec2.describe_addresses()
    unattached_eips = [
        a for a in response['Addresses']
        if 'AssociationId' not in a
    ]
    if unattached_eips:
        # $0.005/hr per unattached EIP = ~$3.60/month
        estimated_cost = len(unattached_eips) * 3.60
        total_monthly_waste += estimated_cost
        savings.append({
            'issue': 'Unattached Elastic IPs',
            'count': len(unattached_eips),
            'monthly_waste': estimated_cost,
            'action': 'Release if not needed - costs $3.60/month each'
        })

    print(f"\nCost Savings Analysis:")
    print("=" * 50)
    if savings:
        for s in savings:
            print(f"  Issue   : {s['issue']}")
            print(f"  Count   : {s['count']}")
            print(f"  Waste   : ${s['monthly_waste']:.2f}/month")
            print(f"  Action  : {s['action']}")
            print()
        print(f"  Total potential savings: ${total_monthly_waste:.2f}/month")
    else:
        print("  No waste detected - resources look clean!")

    return savings, total_monthly_waste


def generate_report(services, total_cost, savings, monthly_waste):
    """Save cost optimization report as JSON."""
    report = {
        'report_date': datetime.now().isoformat(),
        'region': REGION,
        'account_id': ACCOUNT_ID,
        'current_month_cost_usd': round(total_cost, 4),
        'top_services': services[:5],
        'potential_monthly_savings_usd': round(monthly_waste, 2),
        'savings_findings': len(savings)
    }

    filename = f"cost-report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {filename}")
    return filename


def cleanup(budget_name):
    """Delete budget created during this session."""
    budgets = get_budgets_client()
    try:
        budgets.delete_budget(
            AccountId=ACCOUNT_ID,
            BudgetName=budget_name
        )
        print(f"Budget deleted: {budget_name}")
    except Exception as e:
        print(f"Error deleting budget: {e}")


if __name__ == "__main__":
    print("Cost Optimizer - Day 23 of 90")
    print("=" * 50)

    # step 1: get cost breakdown by service
    services, total_cost = get_cost_by_service()

    # step 2: get monthly trend
    get_cost_trend(months=3)

    # step 3: create budget with alerts
    create_budget(BUDGET_NAME, BUDGET_LIMIT, alert_threshold_pct=80)

    # step 4: list all budgets
    list_budgets()

    # step 5: analyze savings opportunities
    savings, monthly_waste = analyze_cost_savings()

    # step 6: generate report
    generate_report(services, total_cost, savings, monthly_waste)

    # step 7: cleanup
    print("\nCleaning up...")
    cleanup(BUDGET_NAME)

    print("\nCost Optimizer complete!")
