import json
import boto3
from botocore.exceptions import ClientError
import urllib.parse

# AWS Client
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Settings
BUCKET = "invoiceaijapantech"
KEY = "Download Your Application.zip"
TABLE_NAME = "DownloadLimits"
MAX_DOWNLOAD = 4
EXPIRE_SECONDS = 86400  # 24 hours

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    method = event.get("httpMethod") or "GET"

    # CORS preflight
    if method == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": ""
        }

  # Reject non-GET requests
    if method != "GET":
        return {
            "statusCode": 405,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Method not allowed"})
        }

    params = event.get("queryStringParameters") or {}
    download_id = params.get("id")
    action = params.get("action", "download")  # status or download

    if not download_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "id is required"})
        }

    try:
        if action == "status":
            # Get current count
            resp = table.get_item(Key={"id": download_id})
            count = resp.get("Item", {}).get("count", 0)
            return {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"count": count})
            }

        elif action == "download":
            # Update count (check maximum)
            try:
                table.update_item(
                    Key={"id": download_id},
                    UpdateExpression="ADD #c :inc",
                    ConditionExpression="attribute_not_exists(#c) OR #c < :max",
                    ExpressionAttributeNames={"#c": "count"},
                    ExpressionAttributeValues={":inc": 1, ":max": MAX_DOWNLOAD}
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    return {
                        "statusCode": 403,
                        "headers": {"Access-Control-Allow-Origin": "*"},
                        "body": json.dumps({"error": "Download limit exceeded"})
                    }
                raise

            # Generate Presigned URL
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET, "Key": KEY},
                ExpiresIn=EXPIRE_SECONDS
            )

            return {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"download_url": presigned_url})
            }

        else:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid action"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
