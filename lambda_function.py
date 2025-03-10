import json
import urllib.parse
import boto3
import csv
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def extract_csv_metadata(bucket, key):
    """Extract metadata from a CSV file stored in S3."""
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8').splitlines()
    
    csv_reader = csv.reader(content)
    column_names = next(csv_reader)  # Extract header
    row_count = sum(1 for _ in csv_reader)  # Count rows excluding header
    file_size = response['ContentLength']
    upload_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'H': key,  # Using 'H' as the primary key
        'upload_timestamp': upload_timestamp,
        'file_size_bytes': file_size,
        'row_count': row_count,
        'column_count': len(column_names),
        'column_names': column_names
    }

def lambda_handler(event, context):
    """Lambda function to process S3 event and store CSV metadata in DynamoDB."""
    table = dynamodb.Table('ulyft_metadata')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        
        if not key.lower().endswith('.csv'):
            print(f"Skipping non-CSV file: {key}")
            continue
        
        try:
            metadata = extract_csv_metadata(bucket, key)
            table.put_item(Item=metadata)
            print(f"Metadata inserted for file: {key}")
        except Exception as e:
            print(f"Error processing file {key}: {str(e)}")
            raise e
