import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Attr, Key

# Convert DynamoDB Decimal objects to native Python types
def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


# Initialize DynamoDB resource and table (outside handler for efficiency)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Sari-cart')  # Replace with your table name


def lambda_handler(event, context):
    # Log the received event for debugging
    print("Received event:", json.dumps(event, indent=2))

    # Extract StudentID from the event
    StudentID = event.get('StudentID')
    if not StudentID:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'StudentID is required'})
        }

    try:
        print("StudentID to be used is:", StudentID)

        # Use scan if no index exists; query is preferred if StudentID is indexed
        response = table.scan(
            FilterExpression=Attr('StudentID').eq(StudentID)
        )

        # Extract and process items
        items = response.get('Items', [])
        items = decimal_to_native(items)

        return {
            'statusCode': 200,
            'body': json.dumps({'items': items})
        }

    except ClientError as e:
        # Handle DynamoDB query errors
        error_message = e.response['Error']['Message']
        print(f"DynamoDB query error: {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error during DynamoDB query',
                'error': error_message
            })
        }

    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An unexpected error occurred',
                'error': str(e)
            })
        }
