import json
import urllib.parse
import boto3
import csv
import chardet  # Auto-detect encoding
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def detect_encoding(content):
    """Detect file encoding using chardet."""
    result = chardet.detect(content)
    return result['encoding']

def extract_csv_metadata(bucket, key):
    """Extract metadata from a CSV file stored in S3."""
    response = s3.get_object(Bucket=bucket, Key=key)
    file_size = response['ContentLength']
    
    if file_size >= 10 * 1024 * 1024:  # 10 MB limit
        print(f"Skipping file {key} as it exceeds 10MB.")
        return None
    
    raw_content = response['Body'].read()
    encoding = detect_encoding(raw_content)

    try:
        decoded_content = raw_content.decode(encoding).splitlines()
    except Exception as e:
        print(f"Error decoding {key} with detected encoding {encoding}: {str(e)}")
        return None
    
    csv_reader = csv.reader(decoded_content)
    
    try:
        column_names = next(csv_reader)  # Extract header
    except StopIteration:
        print(f"Skipping file {key} as it is empty or has no valid header.")
        return None
    
    row_count = sum(1 for _ in csv_reader)  # Count rows excluding header
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
    table = dynamodb.Table('metadata')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        
        if not key.lower().endswith('.csv'):
            print(f"Skipping non-CSV file: {key}")
            continue
        
        try:
            metadata = extract_csv_metadata(bucket, key)
            if metadata:
                table.put_item(Item=metadata)
                print(f"Metadata inserted for file: {key}")
        except Exception as e:
            print(f"Error processing file {key}: {str(e)}")
            raise e
