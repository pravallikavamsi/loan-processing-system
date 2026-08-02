import json
import boto3

# AWS Clients
dynamodb = boto3.resource("dynamodb")
events = boto3.client("events")

# DynamoDB Table
table = dynamodb.Table("LoanApplications")


def lambda_handler(event, context):

    print("Received Event:")
    print(json.dumps(event))

    # Get loan details from EventBridge event
    loan = event["detail"]

    loan_id = loan["loanId"]
    customer_id = loan["customerId"]
    amount = int(loan["amount"])
    loan_type = loan["loanType"]

    # Credit Check Logic
    if amount <= 500000:
        loan_status = "APPROVED"
    elif amount <= 1000000:
        loan_status = "MANUAL_REVIEW"
    else:
        loan_status = "REJECTED"

    # Update DynamoDB
    table.update_item(
        Key={
            "loanId": loan_id
        },
        UpdateExpression="SET loanStatus = :s",
        ExpressionAttributeValues={
            ":s": loan_status
        }
    )

    print(f"Loan {loan_id} updated successfully with status {loan_status}")

    # Publish Loan Status Updated Event
    response = events.put_events(
        Entries=[
            {
                "Source": "loan.credit",
                "DetailType": "LoanStatusUpdated",
                "Detail": json.dumps({
                    "loanId": loan_id,
                    "customerId": customer_id,
                    "amount": amount,
                    "loanType": loan_type,
                    "loanStatus": loan_status
                }),
                "EventBusName": "default"
            }
        ]
    )

    print("EventBridge Response:")
    print(json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "loanId": loan_id,
            "loanStatus": loan_status,
            "message": "Credit Check Completed"
        })
    }
