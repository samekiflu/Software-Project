import boto3
import os

# Optional: use environment variable for table name
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "ModelFeedbackTable")

def write_to_dynamodb(item, table_name=DYNAMODB_TABLE):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    response = table.put_item(Item=item)
    return response
