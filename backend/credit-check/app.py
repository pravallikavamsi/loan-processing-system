import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("LoanApplications")

def lambda_handler(event, context):

    print("Received Event:")
    print(json.dumps(event))

    loan = event["detail"]

    loan_id = loan["loanId"]

    amount = int(loan["amount"])

    if amount <= 500000:

        status = "APPROVED"

    elif amount <= 1000000:

        status = "MANUAL_REVIEW"

    else:

        status = "REJECTED"

    table.update_item(
        Key={
            "loanId": loan_id
        },
        UpdateExpression="SET loanStatus = :s",
        ExpressionAttributeValues={
            ":s": status
        }
    )

    print("Loan Updated")

    return {
        "statusCode": 200,
        "body": json.dumps(status)
    }
