from flask import Flask, jsonify, request, send_file
import boto3
from botocore.exceptions import ClientError
from io import BytesIO
import os
from dotenv import load_dotenv # Add this import

# Load environment variables from a .env file
load_dotenv()

# Retrieve AWS credentials and region from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

app = Flask(__name__)

# Initialize S3 client with credentials from the original script
# In a production environment, consider using IAM roles or environment variables for credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@app.route('/upload/<bucket>/<path:s3_object_key>', methods=['POST'])
def upload_file_to_s3(bucket, s3_object_key):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            s3.upload_fileobj(
                file,
                bucket,
                s3_object_key,
                ExtraArgs={'ContentType': file.content_type} # Optional: set content type
            )
            return jsonify({'message': f'File {file.filename} uploaded successfully to {bucket}/{s3_object_key}'})
        except ClientError as e:
            return jsonify({'error': f'S3 Client Error: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File upload failed'}), 500

@app.route('/list/<bucket>', methods=['GET'])
def list_files_in_bucket(bucket):
    try:
        response = s3.list_objects_v2(Bucket=bucket)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({'files': files})
    except ClientError as e:
        return jsonify({'error': f'S3 Client Error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<bucket>/<path:s3_object_key>', methods=['GET'])
def download_file_from_s3(bucket, s3_object_key):
    try:
        file_obj = BytesIO()
        s3.download_fileobj(bucket, s3_object_key, file_obj)
        file_obj.seek(0)
        
        # Extract original filename from the s3_object_key
        download_name = s3_object_key.split('/')[-1]
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/octet-stream' # Generic MIME type
        )
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return jsonify({'error': f'File not found: {s3_object_key}'}), 404
        return jsonify({'error': f'S3 Client Error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<bucket>/<path:s3_object_key>', methods=['DELETE'])
def delete_file_from_s3(bucket, s3_object_key):
    try:
        s3.delete_object(Bucket=bucket, Key=s3_object_key)
        return jsonify({'message': f'{s3_object_key} deleted successfully from {bucket}'})
    except ClientError as e:
        return jsonify({'error': f'S3 Client Error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5001)