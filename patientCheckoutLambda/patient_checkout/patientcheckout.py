import boto3
import json
import os
import logging


s3 = boto3.client('s3')
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')


logger = logging.getLogger('patientcheckout')
logger.setLevel(logging.INFO)
sns_topic = os.environ.get('SnsTpoicArn')

def lambda_handler(event, context):
    topic = os.environ.get('PATIENT_CHECKOUT_TOPIC')
    TableName = os.environ.get('TableName')
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info('Reading {} from {}'.format(file_key, bucket_name))
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = obj['Body'].read().decode('utf-8')
    checkout_events = json.loads(file_content)
    table = dynamodb.Table(TableName)


    for each_event in checkout_events:
        logger.info('Messaging being published')
        logger.info(each_event)

        # Inserting data into Dynamo DB Table
        #table.put_item(each_event)
        response = table.put_item(TableName=TableName, Item=each_event)
        print("Record has been processed Successfully!!!")
        sns_client.publish(
            TopicArn=topic,
            Message=json.dumps({'default': json.dumps(each_event)}),
            MessageStructure='json'
        )

    sns_client.publish(TopicArn = sns_topic,
    Subject = "Sns Notification",
    Message = "Patient checkout function has been completed successfully...")    


    return {"statusCode":200,
            "body":json.dumps(response)}