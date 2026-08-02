import json
import boto3
import os

sns = boto3.client("sns")

TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

def lambda_handler(event, context):

    print(json.dumps(event))

    loan = event["detail"]

    message = f"""
Loan Submitted Successfully

Loan ID : {loan['loanId']}

Customer : {loan['customerId']}

Amount : {loan['amount']}

Loan Type : {loan['loanType']}
"""

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Loan Application Submitted",
        Message=message
    )

    return {
        "statusCode": 200,
        "body": "Notification Sent"
    }
