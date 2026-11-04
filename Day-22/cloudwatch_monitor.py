import boto3
import os
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
ALARM_EMAIL = os.getenv('ALARM_EMAIL')
ALARM_PREFIX = os.getenv('ALARM_PREFIX', 'devops-journey')


def get_cw_client():
    # CloudWatch client for metrics and alarms
    return boto3.client('cloudwatch', region_name=REGION)


def get_sns_client():
    # SNS client for alarm notifications
    return boto3.client('sns', region_name=REGION)


def create_sns_topic(topic_name):
    """
    Create SNS topic for CloudWatch alarm notifications.

    SNS = Simple Notification Service
    Topic = channel that receives and fans out messages
    Subscription = who gets notified (email, SMS, Lambda, SQS etc)

    Alarm fires -> publishes to SNS topic -> SNS sends email to subscribers
    """
    sns = get_sns_client()

    response = sns.create_topic(Name=topic_name)
    topic_arn = response['TopicArn']
    print(f"SNS topic created: {topic_arn}")

    # subscribe email to topic
    if ALARM_EMAIL:
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=ALARM_EMAIL
        )
        print(f"Email subscribed: {ALARM_EMAIL}")
        print("  Check your email to confirm subscription!")

    return topic_arn


def get_ec2_metrics(hours=1):
    """
    Fetch EC2 CPUUtilization metric for all instances.

    get_metric_statistics() parameters:
    - Namespace  : AWS service category (AWS/EC2, AWS/Lambda etc)
    - MetricName : specific metric to fetch
    - StartTime  : start of time window
    - EndTime    : end of time window
    - Period     : granularity in seconds (300 = 5 minutes)
    - Statistics : Average, Sum, Minimum, Maximum, SampleCount

    Returns list of datapoints sorted by timestamp.
    Empty list = no instances running or no data yet.
    """
    cw = get_cw_client()

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)

    response = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        # no Dimensions = aggregate across all instances
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average', 'Maximum']
    )

    datapoints = sorted(
        response['Datapoints'],
        key=lambda x: x['Timestamp']
    )

    print(f"\nEC2 CPUUtilization (last {hours}h): {len(datapoints)} datapoints")
    for dp in datapoints:
        print(f"  {dp['Timestamp'].strftime('%H:%M')} - "
              f"Avg: {dp['Average']:.2f}% "
              f"Max: {dp['Maximum']:.2f}%")

    if not datapoints:
        print("  No data - no EC2 instances running")

    return datapoints


def get_lambda_metrics(hours=1):
    """
    Fetch Lambda metrics - invocations, errors, duration.

    Lambda metrics available:
    - Invocations : number of times function was called
    - Errors      : number of failed invocations
    - Duration    : execution time in milliseconds
    - Throttles   : invocations rejected due to concurrency limit
    - ConcurrentExecutions : simultaneous executions

    Error rate = Errors / Invocations * 100
    """
    cw = get_cw_client()

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)

    metrics = {}
    for metric_name in ['Invocations', 'Errors', 'Duration']:
        response = cw.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName=metric_name,
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum', 'Average']
        )
        total = sum(dp['Sum'] for dp in response['Datapoints'])
        metrics[metric_name] = total

    print(f"\nLambda Metrics (last {hours}h):")
    print(f"  Invocations : {metrics.get('Invocations', 0):.0f}")
    print(f"  Errors      : {metrics.get('Errors', 0):.0f}")
    print(f"  Duration    : {metrics.get('Duration', 0):.0f}ms total")

    invocations = metrics.get('Invocations', 0)
    errors = metrics.get('Errors', 0)
    if invocations > 0:
        error_rate = (errors / invocations) * 100
        print(f"  Error rate  : {error_rate:.2f}%")

    return metrics


def create_cpu_alarm(alarm_name, topic_arn, threshold=80):
    """
    Create CloudWatch alarm for EC2 CPU utilization.

    Alarm triggers when:
    - CPUUtilization > threshold
    - for 2 consecutive evaluation periods (2 x 5min = 10min sustained)

    ComparisonOperator options:
    - GreaterThanThreshold
    - GreaterThanOrEqualToThreshold
    - LessThanThreshold
    - LessThanOrEqualToThreshold

    EvaluationPeriods = how many periods must breach before alarm fires
    Setting this to 2 prevents false alarms from brief spikes
    """
    cw = get_cw_client()

    cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmDescription=f'CPU utilization exceeds {threshold}% for 10 minutes',
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Statistic='Average',
        # period in seconds - 300 = 5 minutes
        Period=300,
        Threshold=threshold,
        ComparisonOperator='GreaterThanThreshold',
        # 2 periods x 300s = must be high for 10 minutes before alarm
        EvaluationPeriods=2,
        # actions to take when alarm fires
        AlarmActions=[topic_arn],
        # actions to take when alarm returns to OK
        OKActions=[topic_arn],
        # treat missing data as not breaching threshold
        TreatMissingData='notBreaching'
    )
    print(f"CPU alarm created: {alarm_name} (threshold: {threshold}%)")


def create_lambda_error_alarm(alarm_name, topic_arn, threshold=5):
    """
    Create alarm for Lambda error count.

    Monitors Lambda errors across all functions.
    Fires if more than threshold errors in one 5-minute period.
    """
    cw = get_cw_client()

    cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmDescription=f'Lambda errors exceed {threshold} in 5 minutes',
        Namespace='AWS/Lambda',
        MetricName='Errors',
        Statistic='Sum',
        Period=300,
        Threshold=threshold,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        AlarmActions=[topic_arn],
        TreatMissingData='notBreaching'
    )
    print(f"Lambda error alarm created: {alarm_name} (threshold: {threshold} errors)")


def list_alarms():
    """List all CloudWatch alarms and their current state."""
    cw = get_cw_client()
    response = cw.describe_alarms()
    alarms = response['MetricAlarms']

    print(f"\nCloudWatch Alarms: {len(alarms)}")
    print("=" * 50)
    for alarm in alarms:
        state = alarm['StateValue']
        # visual indicator for state
        indicator = 'OK' if state == 'OK' else 'ALARM' if state == 'ALARM' else 'NO DATA'
        print(f"  [{indicator}] {alarm['AlarmName']}")
        print(f"    Metric    : {alarm['MetricName']}")
        print(f"    Threshold : {alarm['ComparisonOperator']} {alarm['Threshold']}")
        print(f"    State     : {state}")

    return alarms


def put_custom_metric(metric_name, value, unit='Count'):
    """
    Publish custom metric to CloudWatch.

    Custom metrics let you monitor your own application data.
    Namespace: use your own name, never AWS/* (reserved for AWS)

    Use cases:
    - track active users
    - monitor queue depth
    - report business metrics (orders/hour)
    - application health score
    """
    cw = get_cw_client()

    cw.put_metric_data(
        # custom namespace - never use AWS/* prefix
        Namespace='DevOpsJourney/Application',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.now(timezone.utc)
        }]
    )
    print(f"Custom metric published: {metric_name} = {value} {unit}")


def generate_report(ec2_metrics, lambda_metrics, alarms):
    """Save monitoring report as JSON."""
    report = {
        'report_date': datetime.now().isoformat(),
        'region': REGION,
        'ec2_cpu_datapoints': len(ec2_metrics),
        'lambda_metrics': lambda_metrics,
        'total_alarms': len(alarms),
        'alarms_in_alarm': len([a for a in alarms if a['StateValue'] == 'ALARM']),
        'alarms_ok': len([a for a in alarms if a['StateValue'] == 'OK'])
    }

    filename = f"cloudwatch-report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {filename}")
    return filename


def cleanup(topic_arn, alarm_names):
    """Delete alarms and SNS topic."""
    cw = get_cw_client()
    sns = get_sns_client()

    cw.delete_alarms(AlarmNames=alarm_names)
    print(f"Alarms deleted: {alarm_names}")

    sns.delete_topic(TopicArn=topic_arn)
    print(f"SNS topic deleted: {topic_arn}")


if __name__ == "__main__":
    print("CloudWatch Monitor - Day 22 of 90")
    print("=" * 50)

    TOPIC_NAME = f"{ALARM_PREFIX}-alerts"
    CPU_ALARM = f"{ALARM_PREFIX}-high-cpu"
    LAMBDA_ALARM = f"{ALARM_PREFIX}-lambda-errors"

    # step 1: create SNS topic for notifications
    topic_arn = create_sns_topic(TOPIC_NAME)

    # step 2: fetch EC2 metrics
    ec2_metrics = get_ec2_metrics(hours=1)

    # step 3: fetch Lambda metrics
    lambda_metrics = get_lambda_metrics(hours=1)

    # step 4: create alarms
    print("\nCreating alarms...")
    create_cpu_alarm(CPU_ALARM, topic_arn, threshold=80)
    create_lambda_error_alarm(LAMBDA_ALARM, topic_arn, threshold=5)

    # step 5: list all alarms
    alarms = list_alarms()

    # step 6: publish custom metric
    print("\nPublishing custom metric...")
    put_custom_metric('DeploymentCount', 1)
    put_custom_metric('HealthScore', 100)

    # step 7: generate report
    generate_report(ec2_metrics, lambda_metrics, alarms)

    # step 8: cleanup
    print("\nCleaning up...")
    cleanup(topic_arn, [CPU_ALARM, LAMBDA_ALARM])

    print("\nCloudWatch Monitor complete!")
