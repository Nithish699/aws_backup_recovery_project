import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv # Add this import
import os

# Load environment variables from a .env file
load_dotenv()

# Retrieve AWS credentials and region from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def backup_file(file_path, bucket_name, object_name):
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"Backup successful: {file_path} → {bucket_name}/{object_name}")
    except ClientError as e:
        print(f"Error: {e}")

# Example usage
backup_file('C:/path/to/file.png', 'your-bucket-name', 'backup_folder/file.png')
