import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# ── Load .env file ─────────────────────────────────────────
load_dotenv()

# ── Read config ────────────────────────────────────────────
REGION = os.getenv('AWS_REGION', 'ap-south-1')
TAG_KEY = os.getenv('EC2_TAG_KEY', 'Environment')
TAG_VALUE = os.getenv('EC2_TAG_VALUE', 'dev')

# Work hours definition
# Instances only run between 9AM and 7PM
WORK_START_HOUR = 9    # 9 AM
WORK_END_HOUR = 19     # 7 PM


def get_dev_instances():
    """
    Get running and stopped dev instances separately.

    Why two separate calls?
    → We need to know which are running (to stop)
    → And which are stopped (to start)
    → One call with both states would mix them together

    Filter by TWO conditions:
    1. Tag = Environment:dev  (only dev instances)
    2. State = running/stopped (only relevant states)
    """
    ec2 = boto3.client('ec2', region_name=REGION)

    # Get RUNNING dev instances
    running_response = ec2.describe_instances(
        Filters=[
            # Filter 1: only dev tagged instances
            {'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]},
            # Filter 2: only running instances
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    # Get STOPPED dev instances
    stopped_response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]},
            {'Name': 'instance-state-name', 'Values': ['stopped']}
        ]
    )

    # Extract instance IDs using list comprehension
    # This replaces a for loop with a shorter expression
    # For each reservation → for each instance → get InstanceId
    running_ids = [
        instance['InstanceId']
        for reservation in running_response['Reservations']
        for instance in reservation['Instances']
    ]

    stopped_ids = [
        instance['InstanceId']
        for reservation in stopped_response['Reservations']
        for instance in reservation['Instances']
    ]

    return running_ids, stopped_ids


def calculate_savings(instance_count, hourly_rate=0.10):
    """
    Calculate monthly savings from scheduler automation.

    Without scheduler:
    → Instances run 24 hours × 30 days = 720 hours/month

    With scheduler (9AM-7PM = 10 hours/day):
    → Instances run 10 hours × 22 workdays = 220 hours/month

    Savings = (720 - 220) × rate × count
    """
    # Hours per month without scheduler
    hours_without = 24 * 30   # 720 hours

    # Work hours per month
    # (WORK_END_HOUR - WORK_START_HOUR) = 10 hours per day
    # × 22 working days per month
    work_hours = (WORK_END_HOUR - WORK_START_HOUR) * 22  # 220 hours

    # Cost = hours × rate per hour × number of instances
    cost_without = hours_without * hourly_rate * instance_count
    cost_with = work_hours * hourly_rate * instance_count
    savings = cost_without - cost_with

    return {
        "instances": instance_count,
        # f-string formats number to 2 decimal places
        "cost_without_scheduler": f"${cost_without:.2f}/month",
        "cost_with_scheduler": f"${cost_with:.2f}/month",
        "monthly_savings": f"${savings:.2f}",
        # Calculate savings percentage
        "savings_percent": f"{(savings/cost_without*100):.0f}%"
    }


def run_scheduler():
    """
    Main scheduler — start or stop based on current time.

    Logic:
    If current hour is between 9 and 19 → work hours → START
    If current hour is outside 9-19    → after hours → STOP

    This simulates what a cron job would do:
    → Run at 9AM  → starts instances
    → Run at 7PM  → stops instances
    """
    # datetime.now().hour returns current hour (0-23)
    current_hour = datetime.now().hour
    current_time = datetime.now().strftime('%H:%M')

    print(f"\n⏰ Scheduler running at: {current_time}")
    print(f"   Work hours: {WORK_START_HOUR}:00 - {WORK_END_HOUR}:00")

    # Get dev instances split by state
    running_ids, stopped_ids = get_dev_instances()

    print(f"\n📊 Dev instances ({TAG_KEY}={TAG_VALUE}):")
    print(f"   Running : {len(running_ids)}")
    print(f"   Stopped : {len(stopped_ids)}")

    ec2 = boto3.client('ec2', region_name=REGION)

    # Decision: are we in work hours?
    if WORK_START_HOUR <= current_hour < WORK_END_HOUR:
        # Inside work hours → START stopped instances
        print(f"\n✅ Work hours — starting stopped instances...")

        if stopped_ids:
            response = ec2.start_instances(InstanceIds=stopped_ids)
            for item in response['StartingInstances']:
                print(f"   ▶️  {item['InstanceId']}: "
                      f"{item['PreviousState']['Name']} → "
                      f"{item['CurrentState']['Name']}")
        else:
            print("   No stopped instances to start")
            print("   (Would start dev instances in a real account)")

    else:
        # Outside work hours → STOP running instances
        print(f"\n🌙 After hours — stopping running instances...")

        if running_ids:
            response = ec2.stop_instances(InstanceIds=running_ids)
            for item in response['StoppingInstances']:
                print(f"   ⏹️  {item['InstanceId']}: "
                      f"{item['PreviousState']['Name']} → "
                      f"{item['CurrentState']['Name']}")
        else:
            print("   No running instances to stop")
            print("   (Would stop dev instances in a real account)")

    # Show savings calculation regardless of instance count
    # Use 5 as example if no instances found
    example_count = max(len(running_ids) + len(stopped_ids), 5)
    savings = calculate_savings(example_count)

    print(f"\n💰 Cost Savings Analysis ({example_count} instances):")
    print(f"   Without scheduler : {savings['cost_without_scheduler']}")
    print(f"   With scheduler    : {savings['cost_with_scheduler']}")
    print(f"   Monthly savings   : {savings['monthly_savings']}")
    print(f"   Savings %         : {savings['savings_percent']}")


if __name__ == "__main__":
    print("⏰ EC2 Scheduler — Day 17 of 90")
    print("=" * 60)
    print("Automates EC2 start/stop based on work hours")
    print(f"Tag filter: {TAG_KEY}={TAG_VALUE}")

    run_scheduler()

    print("\n✅ Scheduler complete!")