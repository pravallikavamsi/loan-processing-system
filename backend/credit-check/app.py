import json
import boto3
import random

dynamodb = boto3.resource("dynamodb")
events = boto3.client("events")

table = dynamodb.Table("LoanApplications")


def lambda_handler(event, context):

    print(json.dumps(event))

    detail = event["detail"]

    loan_id = detail["loanId"]

    amount = detail["amount"]

    score = random.randint(300, 900)

    if score >= 650:
        status = "APPROVED"
    else:
        status = "REJECTED"

    table.update_item(
        Key={
            "loanId": loan_id
        },
        UpdateExpression="SET creditScore=:score, loanStatus=:status",
        ExpressionAttributeValues={
            ":score": score,
            ":status": status
        }
    )

    events.put_events(
        Entries=[
            {
                "Source": "loan.credit",
                "DetailType": "CreditChecked",
                "Detail": json.dumps({
                    "loanId": loan_id,
                    "customerId": detail["customerId"],
                    "amount": amount,
                    "creditScore": score,
                    "status": status
                }),
                "EventBusName": "default"
            }
        ]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Credit Check Completed",
            "loanId": loan_id,
            "status": status,
            "creditScore": score
        })
    }
