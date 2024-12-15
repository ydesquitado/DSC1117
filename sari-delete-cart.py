import boto3
import json
from botocore.exceptions import ClientError

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Lambda function to delete an item from the Sari-cart DynamoDB table.
    Event must include the OrderID (partition key).
    """
    # DynamoDB Table Name
    table_name = "Sari-cart"
    table = dynamodb.Table(table_name)

    try:
        # Parse request body (assumes JSON payload)
        body = json.loads(event.get('body', '{}'))

        # Extract required field
        order_id = body['OrderID']

        # Delete item from DynamoDB
        response = table.delete_item(
            Key={
                'OrderID': order_id
            }
        )

        # Check response for successful deletion
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f'OrderID {order_id} successfully deleted from Sari-cart'})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to delete item from Sari-cart'})
            }

    except KeyError:
        # Missing OrderID in request
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required field: OrderID'})
        }

    except ClientError as e:
        # DynamoDB error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': e.response['Error']['Message']})
        }

    except Exception as e:
        # General error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
