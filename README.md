# Event-Driven Loan Processing System on AWS

## Overview

The Event-Driven Loan Processing System is a cloud-native microservices application built using AWS serverless services. It demonstrates how to design loosely coupled, event-driven applications using Amazon EventBridge.

The application allows customers to submit loan applications through a web interface. Once submitted, the application is processed asynchronously through multiple microservices that perform credit evaluation and send email notifications.

This project demonstrates modern cloud architecture using AWS Lambda, API Gateway, EventBridge, DynamoDB, SNS, Docker, Amazon ECR and S3.

---

# Architecture

```
                                   User
                                     │
                                     ▼
                     S3 Static Website (HTML/CSS/JavaScript)
                                     │
                             HTTP POST Request
                                     │
                                     ▼
                              Amazon API Gateway
                                     │
                                     ▼
                      Submit Loan Lambda (Docker Image)
                                     │
             ┌───────────────────────┼─────────────────────────┐
             │                       │                         │
             ▼                       ▼                         ▼
        Amazon DynamoDB          Amazon S3              Amazon EventBridge
     (Store Loan Details)   (Optional Documents)        LoanSubmitted Event
                                                               │
                                                               ▼
                                          Credit Check Lambda (Docker Image)
                                                               │
                             ┌─────────────────────────────────┴────────────────────────────────┐
                             │                                                                  │
                             ▼                                                                  ▼
                     Update DynamoDB                                                Publish LoanStatusUpdated
                  (loanStatus = APPROVED/                                            Event to EventBridge
                  MANUAL_REVIEW/REJECTED)                                                     │
                                                                                              ▼
                                                                              Approval Notification Lambda
                                                                                              │
                                                                                              ▼
                                                                                       Amazon SNS Topic
                                                                                              │
                                                                                              ▼
                                                                                     Email Notification
```

---

# Project Workflow

## Step 1 – Customer submits loan

The customer opens the web application hosted in Amazon S3.

The frontend sends a POST request to Amazon API Gateway.

Example Request

```json
{
  "customerId": "LOAN101",
  "amount": 450000,
  "loanType": "Car"
}
```

---

## Step 2 – Submit Loan Lambda

Responsibilities

* Generates unique Loan ID
* Stores loan in DynamoDB
* Sets status as SUBMITTED
* Publishes LoanSubmitted event to EventBridge

DynamoDB Item

```json
{
  "loanId": "12345",
  "customerId": "LOAN101",
  "amount": 450000,
  "loanType": "Car",
  "loanStatus": "SUBMITTED",
  "createdAt": "2026-08-03T10:00:00"
}
```

Published Event

```json
{
  "source": "loan.application",
  "detail-type": "LoanSubmitted",
  "detail": {
    "loanId": "12345",
    "customerId": "LOAN101",
    "amount": 450000,
    "loanType": "Car",
    "loanStatus": "SUBMITTED"
  }
}
```

---

## Step 3 – Credit Check Lambda

Triggered automatically by EventBridge.

Business Logic

```
Amount <= 500000
        APPROVED

500001 – 1000000
        MANUAL_REVIEW

Above 1000000
        REJECTED
```

Updates DynamoDB

```
loanStatus = APPROVED
```

Publishes EventBridge Event

```json
{
  "source": "loan.credit",
  "detail-type": "LoanStatusUpdated",
  "detail": {
    "loanId": "12345",
    "customerId": "LOAN101",
    "amount": 450000,
    "loanType": "Car",
    "loanStatus": "APPROVED"
  }
}
```

---

## Step 4 – Approval Notification Lambda

Triggered only for approved loans.

EventBridge Rule

```
Source

loan.credit

Detail Type

LoanStatusUpdated

loanStatus

APPROVED
```

Lambda publishes message to Amazon SNS.

Example Email

```
Subject

Loan Approved

Body

Congratulations!

Your loan has been approved.

Loan ID : 12345

Customer : LOAN101

Amount : 450000

Loan Type : Car

Loan Status : APPROVED
```

---

# AWS Services Used

## Amazon S3

* Static website hosting
* Frontend deployment
* Optional document storage

---

## Amazon API Gateway

* REST API
* HTTP POST endpoint
* CORS enabled
* Invokes Submit Loan Lambda

---

## AWS Lambda

### Submit Loan Lambda

Responsibilities

* Accept loan request
* Generate Loan ID
* Store data
* Publish LoanSubmitted event

---

### Credit Check Lambda

Responsibilities

* Evaluate loan
* Update DynamoDB
* Publish LoanStatusUpdated event

---

### Approval Notification Lambda

Responsibilities

* Receive approved loan event
* Publish email through SNS

---

## Amazon EventBridge

Used for asynchronous communication between microservices.

Events

```
LoanSubmitted

LoanStatusUpdated
```

Advantages

* Loose coupling
* Event filtering
* Easy scalability
* Independent services

---

## Amazon DynamoDB

Table

```
LoanApplications
```

Primary Key

```
loanId
```

Attributes

* loanId
* customerId
* amount
* loanType
* loanStatus
* createdAt

---

## Amazon SNS

Used for sending email notifications.

Topics

```
loan-submitted-topic

approval-notification
```

Subscriptions

* Email

---

## Amazon ECR

Stores Docker container images for Lambda functions.

Repositories

```
submit-loan

credit-check

approval-notification
```

---

## Docker

Each Lambda is packaged as a container image.

Example Dockerfile

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]
```

---

# Event Flow

```
Loan Submitted

↓

EventBridge

↓

Credit Check

↓

LoanStatusUpdated

↓

Approval Notification

↓

SNS

↓

Email
```

---

# Project Structure

```
loan-processing-system/

│

├── frontend/

│      ├── index.html

│      ├── style.css

│      └── app.js

│

├── submit-loan/

│      ├── app.py

│      ├── Dockerfile

│      └── requirements.txt

│

├── credit-check/

│      ├── app.py

│      ├── Dockerfile

│      └── requirements.txt

│

├── approval-notification/

│      ├── app.py

│      ├── Dockerfile

│      └── requirements.txt

│

└── README.md
```

---

# Security

* IAM Roles for each Lambda
* Least-privilege permissions
* EventBridge permissions
* SNS publish permissions
* DynamoDB access control
* API Gateway CORS configuration

---

# Benefits of EventBridge

Instead of direct Lambda-to-Lambda communication,

```
Submit Loan

↓

Credit Check

↓

Notification
```

the project uses

```
Submit Loan

↓

EventBridge

↓

Credit Check

↓

EventBridge

↓

Notification
```

Benefits

* Loose coupling
* Independent microservices
* Easy maintenance
* Better scalability
* Add new consumers without changing existing code
* Event filtering
* Production-ready architecture

---

# Future Enhancements

* Manual Review Notification
* Loan Rejection Notification
* AWS Step Functions
* Amazon SQS Dead Letter Queue (DLQ)
* CloudWatch Dashboard
* CloudWatch Alarms
* AWS X-Ray Tracing
* Terraform Infrastructure as Code
* GitHub Actions CI/CD
* Amazon Cognito Authentication
* Loan Document Upload to Amazon S3
* Audit Logging
* AWS Secrets Manager
* AWS KMS Encryption
* Multi-environment deployments (Dev, QA, Prod)

---

# Technologies

* Python
* AWS Lambda
* Amazon API Gateway
* Amazon DynamoDB
* Amazon EventBridge
* Amazon SNS
* Amazon ECR
* Amazon S3
* Docker
* HTML
* CSS
* JavaScript

---

# Outcomes

This project demonstrates:

* Serverless application development
* Event-driven architecture
* AWS microservices design
* Docker-based Lambda deployments
* REST API development
* NoSQL database integration
* Email notification workflows
* Cloud-native application design
* Asynchronous processing using EventBridge
* Production-style AWS service integration
