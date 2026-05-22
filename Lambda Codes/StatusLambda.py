import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DYNAMODB_TABLE_NAME')

def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        file_id = params.get("file_id")

        if not file_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "file_id is required"})
            }

        response = table.get_item(Key={"file_id": file_id})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Not found"})
            }

        # FIX: convert Decimal → native types
        item = decimal_to_native(item)

        return {
            "statusCode": 200,
            "body": json.dumps(item)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
