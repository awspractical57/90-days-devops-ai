import boto3
import os
import json
import zipfile
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv('AWS_REGION', 'ap-south-1')
ROLE_NAME = os.getenv('LAMBDA_ROLE_NAME', 'DevOpsLambdaRole')
FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'devops-health-checker')


def get_lambda_client():
    # Lambda client for function operations
    return boto3.client('lambda', region_name=REGION)


def get_iam_client():
    # IAM client for role operations
    return boto3.client('iam')


def create_lambda_role(role_name):
    """
    Create IAM role that Lambda service can assume.

    Lambda needs a role to:
    - Write logs to CloudWatch
    - Access other AWS services (S3, DynamoDB etc)

    Trust policy says: lambda.amazonaws.com can assume this role.
    Without this trust policy, Lambda cannot use the role.
    """
    iam = get_iam_client()

    # trust policy - who can assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }

    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Lambda execution role - Day 21'
        )
        role_arn = response['Role']['Arn']
        print(f"Role created: {role_arn}")

        # attach basic execution policy - allows Lambda to write logs
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print("Basic execution policy attached")

        # wait for role to propagate across AWS
        # without this wait, create_function fails with InvalidParameterValueException
        print("Waiting 15 seconds for role to propagate...")
        time.sleep(15)

        return role_arn

    except Exception as e:
        if 'EntityAlreadyExists' in str(e):
            # role already exists, get its ARN
            response = iam.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(f"Role already exists: {role_arn}")
            return role_arn
        print(f"Error creating role: {e}")
        return None


def create_zip_package(function_code, zip_filename):
    """
    Package Python code as zip file for Lambda deployment.

    Lambda requires code to be uploaded as zip.
    The zip must contain the Python file at root level.
    handler format: filename.function_name
    so health_checker.py with lambda_handler becomes:
    handler = health_checker.lambda_handler
    """
    # write the function code to a py file
    py_filename = zip_filename.replace('.zip', '.py')
    with open(py_filename, 'w') as f:
        f.write(function_code)

    # create zip containing the py file
    with zipfile.ZipFile(zip_filename, 'w') as zf:
        # arcname sets the name inside the zip
        # without arcname, full path is included which breaks Lambda
        zf.write(py_filename, arcname=py_filename)

    print(f"Zip package created: {zip_filename}")
    return zip_filename


def create_lambda_function(function_name, role_arn, zip_filename, handler):
    """
    Create Lambda function from zip package.

    runtime = which language/version to use
    handler = filename.function_name (entry point)
    timeout = max seconds function can run (default 3, max 900)
    memory_size = MB of RAM allocated (affects CPU too)
    """
    lmb = get_lambda_client()

    # read zip file as bytes
    with open(zip_filename, 'rb') as f:
        zip_bytes = f.read()

    try:
        response = lmb.create_function(
            FunctionName=function_name,
            # python3.11 = runtime version
            Runtime='python3.11',
            Role=role_arn,
            # handler format: filename.function_name
            Handler=handler,
            Code={'ZipFile': zip_bytes},
            Description='DevOps health checker - Day 21',
            # timeout in seconds - function stops after this
            Timeout=30,
            # memory in MB - more memory = more CPU = faster = more cost
            MemorySize=128
        )
        print(f"Function created: {function_name}")
        print(f"  Runtime : {response['Runtime']}")
        print(f"  Memory  : {response['MemorySize']}MB")
        print(f"  Timeout : {response['Timeout']}s")
        # wait until function is active before returning
        # Pending = being created, Active = ready to invoke
        waiter = lmb.get_waiter('function_active')
        waiter.wait(FunctionName=function_name)
        print(f"  Status  : Active (ready to invoke)")
        return response['FunctionArn']

    except Exception as e:
        print(f"Error creating function: {e}")
        return None


def invoke_lambda(function_name, payload):
    """
    Invoke Lambda function and get response.

    InvocationType options:
    - RequestResponse = synchronous, wait for result (default)
    - Event = asynchronous, fire and forget
    - DryRun = validate permissions only

    Response contains:
    - StatusCode = HTTP status (200 = success)
    - Payload = function return value as stream
    - LogResult = last 4KB of logs (if LogType=Tail)
    """
    lmb = get_lambda_client()

    try:
        response = lmb.invoke(
            FunctionName=function_name,
            # RequestResponse = wait for function to finish
            InvocationType='RequestResponse',
            # LogType=Tail returns last 4KB of logs in response
            LogType='Tail',
            # payload must be bytes
            Payload=json.dumps(payload).encode('utf-8')
        )

        # read the streaming response body
        result = json.loads(response['Payload'].read())

        print(f"\nFunction invoked successfully!")
        print(f"  Status code : {response['StatusCode']}")
        print(f"  Response    : {json.dumps(result, indent=2)}")

        return result

    except Exception as e:
        print(f"Error invoking function: {e}")
        return None


def update_lambda_code(function_name, zip_filename):
    """
    Update existing Lambda function with new code.

    update_function_code() replaces the zip package.
    No need to delete and recreate the function.
    New code is live within seconds.
    """
    lmb = get_lambda_client()

    with open(zip_filename, 'rb') as f:
        zip_bytes = f.read()

    try:
        response = lmb.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes
        )
        print(f"Function code updated: {function_name}")
        print(f"  Last modified: {response['LastModified']}")
        return True
    except Exception as e:
        print(f"Error updating function: {e}")
        return False


def list_functions():
    """List all Lambda functions in the account."""
    lmb = get_lambda_client()
    response = lmb.list_functions()
    functions = response['Functions']

    print(f"\nLambda Functions in {REGION}: {len(functions)}")
    print("=" * 50)
    for f in functions:
        print(f"  Name    : {f['FunctionName']}")
        print(f"  Runtime : {f['Runtime']}")
        print(f"  Memory  : {f['MemorySize']}MB")
        print(f"  Timeout : {f['Timeout']}s")
        print(f"  Modified: {f['LastModified']}")
        print(f"  {'─'*40}")

    return functions


def cleanup(function_name, role_name, zip_filename):
    """Delete Lambda function and IAM role."""
    lmb = get_lambda_client()
    iam = get_iam_client()

    try:
        lmb.delete_function(FunctionName=function_name)
        print(f"Function deleted: {function_name}")
    except Exception as e:
        print(f"Error deleting function: {e}")

    try:
        iam.detach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        iam.delete_role(RoleName=role_name)
        print(f"Role deleted: {role_name}")
    except Exception as e:
        print(f"Error deleting role: {e}")

    # cleanup local files
    import os
    for f in [zip_filename, zip_filename.replace('.zip', '.py')]:
        if os.path.exists(f):
            os.remove(f)
    print("Local files cleaned up")


if __name__ == "__main__":
    print("Lambda Manager - Day 21 of 90")
    print("=" * 50)

    ZIP_FILE = "health_checker.zip"
    HANDLER = "health_checker.lambda_handler"

    # function code as string
    function_code = '''
import json
import datetime

def lambda_handler(event, context):
    # event = data passed when function is triggered
    # context = AWS runtime info (remaining time, memory etc)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Health check passed",
            "day": "Day 21 of 90",
            "topic": "AWS Lambda",
            "timestamp": datetime.datetime.now().isoformat(),
            "event_received": event
        })
    }
'''

    # step 1: create IAM role
    role_arn = create_lambda_role(ROLE_NAME)
    if not role_arn:
        exit(1)

    # step 2: create zip package
    create_zip_package(function_code, ZIP_FILE)

    # step 3: create Lambda function
    function_arn = create_lambda_function(FUNCTION_NAME, role_arn, ZIP_FILE, HANDLER)
    if not function_arn:
        cleanup(FUNCTION_NAME, ROLE_NAME, ZIP_FILE)
        exit(1)

    # step 4: invoke function
    print("\nInvoking function...")
    invoke_lambda(FUNCTION_NAME, {
        "source": "boto3-test",
        "day": 21,
        "timestamp": datetime.now().isoformat()
    })

    # step 5: list all functions
    list_functions()

    # step 6: cleanup
    print("\nCleaning up...")
    cleanup(FUNCTION_NAME, ROLE_NAME, ZIP_FILE)

    print("\nLambda Manager complete!")
