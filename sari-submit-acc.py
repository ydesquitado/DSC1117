import boto3
import json
from botocore.exceptions import ClientError

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    AWS Lambda function to add a new user to the Sari-accounts DynamoDB table.
    Expected input:
    {
        "StudentID": "12345",
        "Username": "johndoe",
        "UserTag": 1,
        "FirstName": "John",
        "LastName": "Doe",
        "Password": "securepassword123"
    }
    """
    # Specify the table name
    table_name = "Sari-accounts"
    table = dynamodb.Table(table_name)

    try:
        # Parse the input from the event
        body = json.loads(event.get('body', '{}'))

        # Extract required fields
        student_id = body['StudentID']
        username = body['Username']
        user_tag = int(body['UserTag'])  # Ensure it's an integer
        first_name = body['FirstName']
        last_name = body['LastName']
        password = body['Password']

        # Put item into DynamoDB
        table.put_item(
            Item={
                'StudentID': student_id,
                'Username': username,
                'UserTag': user_tag,
                'FirstName': first_name,
                'LastName': last_name,
                'Password': password
            }
        )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User successfully added', 'StudentID': student_id})
        }

    except KeyError as e:
        # Handle missing fields
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing required field: {str(e)}'})
        }

    except ClientError as e:
        # Handle DynamoDB client errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': e.response['Error']['Message']})
        }

    except Exception as e:
        # Handle general errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
