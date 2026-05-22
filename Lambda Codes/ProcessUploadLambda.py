import json
import boto3
from urllib.parse import unquote_plus
from datetime import datetime, timezone

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DYNAMODB_TABLE_NAME')
cloudwatch = boto3.client('cloudwatch')


def lambda_handler(event, context):
    """
    Triggered by SQS → contains S3 event.
    Processes each record independently with partial failure handling.
    """

    failures = []

    for record in event.get('Records', []):
        file_id = None

        try:
            # --- Extract SQS body ---
            body = json.loads(record['body'])

            if 'Records' not in body or not body['Records']:
                raise Exception("Invalid S3 event structure")

            s3_record = body['Records'][0]

            bucket = s3_record['s3']['bucket']['name']
            key = unquote_plus(s3_record['s3']['object']['key'])

            # --- Extract identifiers ---
            file_name = key.split("/")[-1]
            file_id = file_name.split(".")[0]

            # --- Fetch metadata ---
            response = s3.head_object(Bucket=bucket, Key=key)

            size = response.get('ContentLength')
            content_type = response.get('ContentType', 'unknown')
            last_modified = response.get('LastModified')

            last_modified_str = (
                last_modified.isoformat() if last_modified else None
            )

            now = datetime.now(timezone.utc).isoformat()

            # --- Store success ---
            table.put_item(
                Item={
                    "file_id": file_id,
                    "status": "PROCESSED",
                    "file_name": file_name,
                    "bucket": bucket,
                    "key": key,
                    "size": size,
                    "content_type": content_type,
                    "last_modified": last_modified_str,
                    "processed_at": now
                }
            )

            # --- Metric: success ---
            cloudwatch.put_metric_data(
                Namespace='METRIC_NAME',
                MetricData=[
                    {
                        'MetricName': 'FilesProcessed',
                        'Value': 1,
                        'Unit': 'Count'
                    }
                ]
            )

            print(json.dumps({
                "level": "INFO",
                "action": "PROCESS_FILE",
                "file_id": file_id,
                "status": "PROCESSED"
            }))

        except Exception as e:
            print(json.dumps({
                "level": "ERROR",
                "file_id": file_id,
                "error": str(e)
            }))

            now = datetime.now(timezone.utc).isoformat()

            # --- Store failure ---
            table.put_item(
                Item={
                    "file_id": file_id if file_id else "unknown",
                    "status": "FAILED",
                    "error": str(e),
                    "processed_at": now
                }
            )

            # --- Metric: failure ---
            cloudwatch.put_metric_data(
                Namespace='METRIC_NAME',
                MetricData=[
                    {
                        'MetricName': 'FilesFailed',
                        'Value': 1,
                        'Unit': 'Count'
                    }
                ]
            )

            # --- Mark this message as failed (partial batch response) ---
            failures.append({
                "itemIdentifier": record["messageId"]
            })

    # --- Return partial batch response ---
    return {
        "batchItemFailures": failures
    }
