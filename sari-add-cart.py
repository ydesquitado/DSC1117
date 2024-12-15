import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        # Retrieve table name from the event
        table_name = event.get("Table")
        if not table_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Table name is required in the input.'})
            }
        
        # Access the specified DynamoDB table
        table = dynamodb.Table(table_name)
        
        # Perform a scan operation
        response = table.scan()
        items = response.get('Items', [])
        
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
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
