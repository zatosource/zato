# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class AWSPing(Service):
    """ Pings an AWS connection and returns the caller's account ID.
    """
    name = 'test.aws.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.aws[conn_name]
        identity = conn.ping()

        self.response.payload = json.dumps({'account': identity['Account']})

# ################################################################################################################################
# ################################################################################################################################

class AWSS3RoundTrip(Service):
    """ Creates an S3 bucket, stores an object in it and reads the object back.
    """
    name = 'test.aws.s3-roundtrip'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request
        conn_name = raw_request['conn_name']
        bucket = raw_request['bucket']
        key = raw_request['key']
        data = raw_request['data']

        # Get the connection by its name ..
        conn = self.aws[conn_name]

        # .. create the bucket and store the object ..
        _ = conn.s3.create_bucket(Bucket=bucket)
        _ = conn.s3.put_object(Bucket=bucket, Key=key, Body=data.encode('utf8'))

        # .. read the object back ..
        response = conn.s3.get_object(Bucket=bucket, Key=key)
        body = response['Body'].read()

        # .. list all the buckets we can see ..
        list_response = conn.s3.list_buckets()

        bucket_names = []
        for item in list_response['Buckets']:
            bucket_names.append(item['Name'])

        # .. and hand everything back to the caller.
        self.response.payload = json.dumps({'data': body.decode('utf8'), 'buckets': bucket_names})

# ################################################################################################################################
# ################################################################################################################################

class AWSSQSRoundTrip(Service):
    """ Creates an SQS queue, sends a message to it and receives the message back.
    """
    name = 'test.aws.sqs-roundtrip'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request
        conn_name = raw_request['conn_name']
        queue_name = raw_request['queue_name']
        message_body = raw_request['message_body']

        # Get the connection by its name ..
        conn = self.aws[conn_name]

        # .. create the queue ..
        create_response = conn.sqs.create_queue(QueueName=queue_name)
        queue_url = create_response['QueueUrl']

        # .. publish the message ..
        _ = conn.sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)

        # .. receive it back ..
        receive_response = conn.sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        message = receive_response['Messages'][0]

        # .. remove it from the queue ..
        _ = conn.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])

        # .. and hand the received body back to the caller.
        self.response.payload = json.dumps({'message_body': message['Body']})

# ################################################################################################################################
# ################################################################################################################################

class AWSDynamoDBRoundTrip(Service):
    """ Creates a DynamoDB table, stores an item in it and reads the item back through the resource API.
    """
    name = 'test.aws.dynamodb-roundtrip'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request
        conn_name = raw_request['conn_name']
        table_name = raw_request['table_name']
        customer_id = raw_request['customer_id']
        customer_name = raw_request['customer_name']

        # Get the connection by its name ..
        conn = self.aws[conn_name]

        # .. create the table through the low-level client ..
        _ = conn.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST',
        )

        # .. store and read the item back through the resource API ..
        dynamodb_resource = conn.resource('dynamodb')
        table = dynamodb_resource.Table(table_name)

        _ = table.put_item(Item={'customer_id': customer_id, 'name': customer_name})
        response = table.get_item(Key={'customer_id': customer_id})
        item = response['Item']

        # .. and hand the item back to the caller.
        self.response.payload = json.dumps({'customer_id': item['customer_id'], 'name': item['name']})

# ################################################################################################################################
# ################################################################################################################################
