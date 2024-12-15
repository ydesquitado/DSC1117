import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

# Utility function to convert Decimal objects to native Python types
def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Parse the body if it exists
        body = event.get("body")
        if body:
            try:
                print("Raw body:", body)  # Log raw body for debugging
                body = json.loads(body)  # Parse the JSON string into a dictionary
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON format in request body.'})
                }
        else:
            body = {}  # Default to an empty dictionary if body is not provided

        # Ensure body is a dictionary
        if not isinstance(body, dict):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request format. Body must be a JSON object.'})
            }
        
        # Get the table name
        table_name = "Sari-accounts"
        if not table_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Table name is required in the input.'})
            }
        
        # Access the DynamoDB table
        table = dynamodb.Table(table_name)
        
        # Perform a scan operation
        response = table.scan()
        items = response.get('Items', [])
        
        # Convert items to JSON-serializable format
        items = decimal_to_native(items)
        
        # Return the fetched data
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(items)
        }
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Table "{table_name}" not found.'})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        print("Unexpected error:", str(e))  # Log unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
