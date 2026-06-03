import json
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    iam = boto3.client('iam')
    cloudtrail = boto3.client('cloudtrail')
    
    # Fetch recent events
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    response = cloudtrail.lookup_events(
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=10
    )
    
    events = response['Events']
    print(f"📋 Found {len(events)} events")
    
    # Look for any event where username is 'test-agent' (simulate anomaly)
    anomaly_found = False
    for event in events:
        username = event.get('Username', '')
        if username == 'test-agent':
            anomaly_found = True
            print(f"⚠️ Anomaly detected: {event['EventName']} by {username}")
            break
    
    if anomaly_found:
        # Detach the S3 read-only policy from test-agent
        try:
            iam.detach_user_policy(
                UserName='test-agent',
                PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
            )
            print("✅ Remediation applied: Removed S3ReadOnlyAccess from test-agent")
        except Exception as e:
            print(f"❌ Failed to detach policy: {e}")
    else:
        print("✅ No anomaly detected")
    
    return {
        'statusCode': 200,
        'body': json.dumps("Agent checked and remediated if needed")
    }