import json
import datetime

def lambda_handler(event, context):
    # event = what triggered this function
    # context = runtime information from AWS
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Health check passed',
            'day': 'Day 21 of 90',
            'timestamp': datetime.datetime.now().isoformat(),
            'event_received': event
        })
    }
