import json
import boto3

logs = boto3.client("logs")


def lambda_handler(event, context):

    print(json.dumps(event))

    detail = event["detail"]

    loan_id = detail["loanId"]

    status = detail["status"]

    score = detail["creditScore"]

    message = {
        "loanId": loan_id,
        "status": status,
        "creditScore": score,
        "message": f"Loan {status}"
    }

    print(json.dumps(message))

    return {
        "statusCode": 200,
        "body": json.dumps(message)
    }
