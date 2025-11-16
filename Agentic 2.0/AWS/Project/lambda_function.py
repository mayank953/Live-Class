import json

import boto3
import botocore
import botocore.config
from datetime import datetime
from botocore.exceptions import ClientError

#---------------

REGION = "us-east-1"
MODEL_ID= "anthropic.claude-3-haiku-20240307-v1:0"
S3_Bucket = 'aws-bedrock-project-2'
S3_PREFIX='input/'
TIMEOUT_SECONDS=300

#---------------

client = boto3.client("bedrock-runtime", region_name=REGION)

s3 = boto3.client('s3', region_name=REGION)


def research_via_bedrock(topic):
    # Format the request payload using the model's native structure.
    PROMPT = f"Write a detailed 500 words research report on the {topic}"
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": PROMPT}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=MODEL_ID, body=request)
        return response
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{MODEL_ID}'. Reason: {e}")
        raise RuntimeError(f"ERROR: Can't invoke '{MODEL_ID}'. Reason: {e}")

def save_to_s3(content, bucket, prefix):
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    object_key = f"{prefix}bedrock_response_{timestamp}.txt"

    try:
        s3.put_object(Body=content.encode('utf-8'), Bucket=bucket, Key=object_key)
        print(f"Saved response to s3://{bucket}/{object_key}")
    except ClientError as e:
        print(f"ERROR: Can't save to S3. Reason: {e}")
        raise RuntimeError(f"ERROR: Can't save to S3. Reason: {e}")


def lambda_handler(event, context):
    # TODO implement

    try:

        if(isinstance(event, dict) and 'body' in event and isinstance(event['body'], str)):
            body = json.loads(event['body'])
        else:
            body = event
        
        research_topic = body.get('topic') or body.get('research_topic') 
        if not research_topic:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing research topic in the request')}

        response = research_via_bedrock(research_topic)
        s3_key= save_to_s3(response, S3_Bucket, S3_PREFIX)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Research report generated and saved to S3 successfully.',
                's3_bucket': S3_Bucket,
                's3_key': s3_key
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing request: {e}")
        }
