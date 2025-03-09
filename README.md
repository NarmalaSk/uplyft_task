# Uplifts Task - CSV Extraction Pipeline

## Overview
This project sets up a CSV processing pipeline using **Terraform, LocalStack, Docker, and AWS services**. The pipeline enables users to upload CSV files to an **S3 bucket**, which triggers a **Lambda function** to process the file and store its metadata in **DynamoDB**.

## Prerequisites
Ensure the following are installed and added to the environment path (for Windows users):

- **Terraform**
- **LocalStack**
- **Docker Desktop/Daemon**
- **AWS CLI** (Basic AWS knowledge is required)

### Repository
Find the complete source code here: [GitHub Repository](https://github.com/NarmalaSk/uplyft_task/tree/main)

---
## Pipeline Workflow
1. **User uploads a CSV file** to an S3 bucket.
2. **S3 triggers a Lambda function** upon object creation.
3. **Lambda function processes the file** and stores metadata in **DynamoDB**.

---
## Setup Guide

### 1. Create the Project Directory
```sh
mkdir uplift
cd uplift
```

### 2. Open the Project in VS Code (Windows)
```sh
code .
```

### 3. Create the Lambda Function
```sh
nano lambda_function.py  # For Linux/Mac
notepad lambda_function.py  # For Windows
```
Copy and paste the **lambda_function.py** code from the [GitHub repository](https://github.com/NarmalaSk/uplyft_task/tree/main).

### 4. Package the Lambda Function
- **Windows:**
```powershell
Compress-Archive lambda_function.py -DestinationPath python.zip -Force
```
- **Linux/Mac:**
```sh
zip python.zip lambda_function.py
```

### 5. Create Terraform Configuration
```sh
nano main.tf  # For Linux/Mac
notepad main.tf  # For Windows
```
Copy and paste the **Terraform configuration** from the repository.

---
## Running the Pipeline

### 1. Start LocalStack
```sh
docker daemon &   # Ensure Docker Daemon is running
localstack start  # Start LocalStack
```

### 2. Initialize and Apply Terraform
```sh
cd uplift
terraform init
terraform apply -auto-approve
```

### 3. Upload a CSV File to S3
```sh
awslocal s3 cp sample.csv s3://my-bucket/ --endpoint-url=http://localhost:4566
```

### 4. Verify Processing
- Lambda function should process the file.
- Metadata should be stored in **DynamoDB**.
- Check logs using:
```sh
aws logs tail /aws/lambda/<lambda-function-name> --endpoint-url=http://localhost:4566
```

---
## Error Handling
- Processes **only `.csv` files**.
- Shows error logs if file size exceeds **10MB**.
- Restricts storing non-CSV files in **DynamoDB**.
- Ensures Lambda **triggers only for `.csv` files**.

---
## Conclusion
You have successfully set up a CSV processing pipeline using **Terraform and LocalStack**. 

For any issues, check logs or refer to the [GitHub repository](https://github.com/NarmalaSk/uplyft_task/tree/main). 

