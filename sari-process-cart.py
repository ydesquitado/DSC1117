import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')

# Define your table names
CART = "Sari-cart"
INVENTORY = "Sari-inventory"
ORDERS = "Sari-orders"

def decimal_to_native(obj):
    
    # Convert DynamoDB Decimal objects to native Python types
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    
    return obj

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event, indent=2))
        
        # Parse the incoming event to extract cart information
        StudentID = event['StudentID']  # Unique identifier for the user
        print("StudentID is", StudentID)

        # Fetch the cart items
        cartItems = getCartItems(StudentID)
        cartItems = cartItems.get('Items', [])  # Extract the items list
        print("Cart items:", json.dumps(cartItems, indent=2))

        if not cartItems:
            return {
                'statusCode': 400,
                'body': json.dumps('Cart is empty.')
            }

        # Process the transaction
        OrderID = processTransactions(StudentID, cartItems)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Transaction successful.', 'OrderID': OrderID})
        }

    except Exception as e:
        import traceback
        print("Error occurred:", traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def getCartItems(StudentID):
    try:
        table = dynamodb.Table(CART)
        response = table.scan(
            FilterExpression=Attr('StudentID').eq(StudentID)
        )
        
        # Convert response to native types before returning or logging
        response = decimal_to_native(response)
        print("Response:", json.dumps(response, indent=2))
        return response

    except ClientError as e:
        raise Exception(f"Error fetching cart: {e.response['Error']['Message']}")

def processTransactions(StudentID, cartItems):
    OrderID = generateOrderID()
    try:
        transactItems = []
        for item in cartItems:
            ProductID = item['ProductID']
            Quantity = item['Quantity']
            TotalPrice = sum(item['Price'] * item['Quantity'] for item in cartItems)

            # Fetch current stock for validation
            inventoryTable = dynamodb.Table(INVENTORY)
            inventoryResponse = inventoryTable.get_item(Key={'ProductID': ProductID})
            currentStock = inventoryResponse.get('Item', {}).get('Stock', 0)

            if currentStock < Quantity:
                raise Exception(f"Insufficient stock for ProductID: {ProductID}")

            # Prepare transaction for reducing stock
            transactItems.append({
                'Update': {
                    'TableName': INVENTORY,
                    'Key': {'ProductID': {'S': ProductID}},
                    'UpdateExpression': 'SET Stock = Stock - :Quantity',
                    'ConditionExpression': 'Stock >= :Quantity',
                    'ExpressionAttributeValues': {
                        ':Quantity': {'N': str(Quantity)}
                    }
                }
            })

        # Add transaction for creating an order
        transactItems.append({
            'Put': {
                'TableName': ORDERS,
                'Item': {
                    'OrderID': {'S': OrderID},
                    'OrderDate': {'S': datetime.now().isoformat()},
                    'StudentID': {'S': StudentID},
                    'Cart': {'S': "items"},
                    'TotalPayment': {'N': str(TotalPrice)},
                    'MOP': {'S': "Cash"},
                    'PaymentStatus': {'S': "PAID"},
                    'MOD': {'S': "Pickup"},
                    'Location': {'S': "ADB-405"},
                    'ETA': {'S': "Tomorrow"},
                    'DeliveryStatus': {'S': 'PENDING'}
                }
            }
        })

        # Execute the transaction
        client = boto3.client('dynamodb')
        client.transact_write_items(TransactItems=transactItems)
        return OrderID

    except ClientError as e:
        print(f"Transaction failed: {e.response['Error']['Message']}")
        raise Exception(f"Transaction failed: {e.response['Error']['Message']}")


def generateOrderID():
    # Generates a unique order ID
    import uuid
    return str(uuid.uuid4())