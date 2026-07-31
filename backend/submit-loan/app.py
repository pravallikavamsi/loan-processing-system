import json
import boto3
import uuid
from datetime import datetime


dynamodb = boto3.resource('dynamodb')

events = boto3.client(
    'events'
)

s3 = boto3.client(
    's3'
)


table = dynamodb.Table(
    'LoanApplications'
)


def lambda_handler(event, context):

    body = json.loads(event['body'])


    loan_id = str(uuid.uuid4())


    loan = {

        "loanId": loan_id,

        "customerId": body["customerId"],

        "amount": body["amount"],

        "loanType": body["loanType"],

        "status":"SUBMITTED",

        "createdAt":
        str(datetime.now())

    }


    # Store DynamoDB

    table.put_item(
        Item=loan
    )


    # Store Raw Request

    s3.put_object(

        Bucket="loan-raw-data1",

        Key=f"{loan_id}.json",

        Body=json.dumps(body)

    )


    # Publish Event

    events.put_events(

        Entries=[

        {

        "Source":
        "loan.application",

        "DetailType":
        "LoanSubmitted",

        "Detail":
        json.dumps(loan),

        "EventBusName":
        "default"

        }

        ]

    )


    return {


    "statusCode":200,

    "body":json.dumps({

    "loanId":loan_id,

    "message":
    "Loan Submitted"

    })

    }
