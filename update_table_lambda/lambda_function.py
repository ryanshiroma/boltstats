import json
import boto3
import json
import time
import requests
from mychevy.mychevy import MyChevy

def get_dynamodb_type(value: str) -> str:

    try:
        float(value)
        return 'N'
    except:
        return 'S'

def main(event, context):

    print('pulling ssm credentials...')
    ssm = boto3.client('ssm',region_name='us-east-1')
    parameter = ssm.get_parameter(Name='chevybolt', WithDecryption=True)
    credentials = json.loads(parameter['Parameter']['Value'])
    print('complete')
    try:
        print('retrieving data from MyChevrolet...')
        page = MyChevy(credentials['username'], credentials['password'])
        page.login()
        page.get_cars()
        cars = page.update_cars()
        car_attributes = vars(cars[0])
        print('complete')

        print('packaging payload...')
        payload = {}
        for attribute in car_attributes:
            payload[attribute] = {get_dynamodb_type(str(car_attributes[attribute])): str(car_attributes[attribute])}
        payload['date'] = {'N': str(time.time())}
        print('complete')

        print('writing to dynamodb...')
        dynamodb = boto3.client('dynamodb')
        result = dynamodb.put_item(TableName='chevyBolt', Item=payload)
        print('complete')

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }


if __name__ == "__main__":
    main('', '')
