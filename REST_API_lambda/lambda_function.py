import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import time
from datetime import datetime, timedelta

def lambda_handler(event, context):

    try:
        vin = event['queryStringParameters']['vin']
        limit = event['queryStringParameters'].get('limit', '100')
        after = event['queryStringParameters'].get('after', '1970-01-01')
        before = event['queryStringParameters'].get('before', None)
        
        after = datetime.strptime(after, "%Y-%m-%d").timestamp()
        before = time.time() if before is None else datetime.strptime(before, "%Y-%m-%d").timestamp()
    
        client = boto3.resource('dynamodb')
        table = client.Table("boltstats")
        
        query_response = table.query(
                  Limit = int(limit),
                  ScanIndexForward = False,
                  KeyConditionExpression=Key('vin').eq(vin) 
                    & Key('time').between(Decimal(after),Decimal(before))
              )
        response = {'Items':[]}
        for row in query_response['Items']:
            response['Items'].append({'totalMiles': str(row['totalMiles']),
                                      'totalRange': str(row['totalRange']),
                                      'batteryLevel': str(row['batteryLevel'])})
        response_object = {}
        response_object['statusCode'] = 200
        response_object['headers'] = {'Content-Type':'application/json'}
        response_object['body'] = json.dumps(response)
        
        return response_object

except Exception as e:
    # print(e.response['Error']['Message'])
    return {
        'statusCode': 500,
        'body': 'bad input'
    }
