import json
import boto3
import os

sns = boto3.client("sns")

TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):

    print("Received Event:")
    print(json.dumps(event))

    loan = event["detail"]

    # Only send email for approved loans
    if loan["loanStatus"] != "APPROVED":
        return {
            "statusCode": 200,
            "body": "Loan is not approved. No notification sent."
        }

    message = f"""
Congratulations!

Your loan has been approved.

Loan ID : {loan['loanId']}

Customer : {loan['customerId']}

Amount : {loan['amount']}

Loan Type : {loan['loanType']}

Loan Status : {loan['loanStatus']}

Thank you for choosing our services.
"""

    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Loan Approved",
        Message=message
    )

    print("SNS Response:")
    print(json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Approval Notification Sent",
            "loanId": loan["loanId"],
            "loanStatus": loan["loanStatus"]
        })
    }
