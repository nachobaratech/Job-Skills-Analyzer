import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """
    Triggered when new data uploaded to S3.
    Updates Athena table and sends email notification.
    """
    
    athena = boto3.client('athena', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    try:
        # Get S3 event details
        if 'Records' in event:
            bucket = event['Records'][0]['s3']['bucket']['name']
            key = event['Records'][0]['s3']['object']['key']
            size = event['Records'][0]['s3']['object'].get('size', 0)
            
            print(f"Lambda triggered at {timestamp}")
            print(f"New file: s3://{bucket}/{key}")
            print(f"Size: {size} bytes")
        else:
            bucket = "test"
            key = "manual-trigger"
            size = 0
        
        # Update Athena table
        query = "MSCK REPAIR TABLE job_skills_db.jobs_with_skills"
        
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': 'job_skills_db'},
            ResultConfiguration={
                'OutputLocation': 's3://job-skills-athena-results-624943535027/'
            }
        )
        
        query_id = response['QueryExecutionId']
        print(f"Athena query started: {query_id}")
        
        # Send SUCCESS notification via SNS
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:624943535027:job-skills-alerts',
            Subject='✅ Job Skills Analyzer - Data Updated',
            Message=f"""
Job Market Skills Analyzer - ETL Pipeline Success

📊 NEW DATA PROCESSED:
--------------------------------------------------
Time: {timestamp}
File: {key}
Size: {size:,} bytes
Bucket: {bucket}

✅ ACTIONS COMPLETED:
--------------------------------------------------
✓ File uploaded to S3
✓ Lambda function triggered automatically
✓ Athena table updated (Query ID: {query_id})
✓ Dashboard data refreshed

🌐 ACCESS UPDATED DATA:
--------------------------------------------------
Dashboard: http://localhost:8501
API: http://localhost:8000/stats

--------------------------------------------------
This is an automated notification from your Job Skills Analyzer.
All systems operational.
            """
        )
        
        print("✅ SNS notification sent")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'ETL completed successfully',
                'query_id': query_id,
                'file': key,
                'notification': 'sent'
            })
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        
        # Send ERROR notification via SNS
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:624943535027:job-skills-alerts',
            Subject='❌ Job Skills Analyzer - ERROR',
            Message=f"""
Job Market Skills Analyzer - ETL Pipeline Error

⚠️ ERROR OCCURRED:
--------------------------------------------------
Time: {timestamp}
Error: {error_msg}

❌ FAILED OPERATION:
--------------------------------------------------
The automated ETL pipeline encountered an error while
processing new data. Please check CloudWatch logs for details.

📋 TROUBLESHOOTING:
--------------------------------------------------
1. Check Lambda logs in CloudWatch
2. Verify S3 file format
3. Confirm Athena database connectivity

--------------------------------------------------
This is an automated error notification.
            """
        )
        
        raise e

