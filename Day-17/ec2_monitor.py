import boto3
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')


def get_all_instances():
    """
    Get all non-terminated EC2 instances.

    We filter out 'terminated' instances because:
    → Terminated = permanently deleted
    → No point monitoring deleted instances
    → AWS keeps terminated instances visible for ~1 hour
    """
    ec2 = boto3.client('ec2', region_name=REGION)

    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                # List of states we WANT to see
                # 'not terminated' isn't a valid filter
                # So we list all states EXCEPT terminated
                'Values': ['pending', 'running', 'stopping', 'stopped']
            }
        ]
    )

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = 'No Name'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']

            instances.append({
                'id': instance['InstanceId'],
                'name': name,
                'type': instance['InstanceType'],
                'state': instance['State']['Name'],
                # launch_time tells us when instance was started
                'launch_time': instance.get('LaunchTime', '').isoformat()
                if instance.get('LaunchTime') else 'unknown'
            })

    return instances


def get_cpu_metrics(instance_id):
    """
    Get CPU utilization for an EC2 instance using CloudWatch.

    CloudWatch = AWS monitoring service
    Stores metrics (CPU, network, disk) for all AWS resources

    get_metric_statistics() parameters explained:
    → Namespace: 'AWS/EC2' = EC2 metrics namespace
    → MetricName: 'CPUUtilization' = which metric
    → Dimensions: filter to specific instance
    → StartTime: how far back to look
    → EndTime: up to when
    → Period: 300 = group data in 5-minute chunks
    → Statistics: ['Average'] = calculate average
    """
    # CloudWatch is a separate service from EC2
    cloudwatch = boto3.client('cloudwatch', region_name=REGION)

    # Look at last 1 hour of data
    end_time = datetime.utcnow()
    # timedelta(hours=1) = subtract 1 hour from current time
    start_time = end_time - timedelta(hours=1)

    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,           # 5 minutes in seconds
            Statistics=['Average']
        )

        # Datapoints = list of metric readings
        datapoints = response.get('Datapoints', [])

        if not datapoints:
            return None

        # Get the most recent datapoint
        # sorted() sorts by Timestamp, [-1] gets the last item
        latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]

        # Round to 2 decimal places for readability
        return round(latest['Average'], 2)

    except Exception as e:
        print(f"   ⚠️  CloudWatch error for {instance_id}: {e}")
        return None


def monitor_instances():
    """
    Monitor all instances and generate health report.
    """
    print(f"\n🔍 Monitoring EC2 instances in {REGION}...")
    print("=" * 60)

    instances = get_all_instances()

    if not instances:
        print("   No instances found to monitor")
        return []

    monitoring_results = []

    for instance in instances:
        print(f"\n   📊 {instance['id']} ({instance['name']})")
        print(f"      State : {instance['state']}")
        print(f"      Type  : {instance['type']}")

        result = {
            **instance,  # ** unpacks dict — copies all keys from instance
            'monitored_at': datetime.now().isoformat(),
            'cpu_percent': None,
            'health': 'unknown'
        }

        # Only check CPU for running instances
        # Stopped instances have no CPU metrics
        if instance['state'] == 'running':
            cpu = get_cpu_metrics(instance['id'])

            if cpu is not None:
                result['cpu_percent'] = cpu
                print(f"      CPU   : {cpu}%")

                # Simple health check based on CPU
                if cpu > 80:
                    result['health'] = 'warning'
                    print(f"      Health: ⚠️  WARNING (high CPU)")
                else:
                    result['health'] = 'healthy'
                    print(f"      Health: ✅ healthy")
            else:
                print(f"      CPU   : No data yet")
                result['health'] = 'no_data'
        else:
            # Stopped instance — no CPU to check
            result['health'] = 'stopped'
            print(f"      Health: ⏹️  stopped")

        monitoring_results.append(result)

    return monitoring_results


def save_monitoring_report(results):
    """Save monitoring results to JSON file."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "day": "Day 17 of 90",
        "topic": "EC2 Monitoring with boto3",
        "region": REGION,
        "instance_count": len(results),
        "instances": results
    }

    filename = f"ec2-monitor-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📋 Monitoring report saved: {filename}")
    return filename


if __name__ == "__main__":
    print("🏥 EC2 Monitor — Day 17 of 90")
    print("=" * 60)

    results = monitor_instances()

    if results:
        save_monitoring_report(results)

    print("\n✅ EC2 Monitor complete!")
