import boto3
from botocore.exceptions import ClientError

s3 = boto3.client(
    's3',
    aws_access_key_id='AKIA44Y6CDN4LUMQQMMC',
    aws_secret_access_key='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',
    region_name='us-east-1'
)

def backup_file(file_path, bucket_name, object_name):
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"Backup successful: {file_path} → {bucket_name}/{object_name}")
    except ClientError as e:
        print(f"Error: {e}")

# Example usage
backup_file('C:/path/to/file.png', 'your-bucket-name', 'backup_folder/file.png')
