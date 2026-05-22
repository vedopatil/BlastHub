import json
import boto3
import uuid

s3 = boto3.client('s3')
BUCKET_NAME = "[BUCKET_NAME]" #Real name removed for security reasons

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}

    filename = params.get("filename", "file")

    file_id = str(uuid.uuid4())
    ext = filename.split('.')[-1] if '.' in filename else ''

    key = f"uploads/raw/{file_id}.{ext}" if ext else f"uploads/raw/{file_id}"

    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key
        },
        ExpiresIn=300
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "file_id": file_id,
            "uploadUrl": url,
            "key": key
        })
    }
