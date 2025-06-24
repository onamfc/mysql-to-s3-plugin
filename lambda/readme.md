# AWS Lambda Deployment Guide

This guide explains how to package and deploy the MySQL-to-S3 export logic as an AWS Lambda function using the zip method (no Docker required).

## Overview
The Lambda function uses the same logic as the main script but wraps it in an AWS-compatible handler. The function:
 - Connects to your MySQL database
 - Fetches data in chunks
 - Converts the data to Parquet
 - Uploads grouped files to your S3 bucket

## Prerequisites
 - AWS CLI configured with sufficient permissions
 - Python 3.7 or later
 - IAM Role for Lambda with:
    - AmazonS3FullAccess or scoped access to your bucket
    - Access to Secrets Manager or RDS (optional)
 - A Lambda-compatible .env file with credentials (or use AWS environment variables)

## Packaging the Lambda Function
1. **Install dependencies into a build directory**:
   ```
    mkdir -p lambda/build
    pip install -r lambda/lambda_requirements.txt -t lambda/build/
   ```
2. **Copy function code and supporting files**:
    ```
   cp lambda/handler.py main.py .env lambda/build/
   ```
3. **Zip the Lambda package**
    ```
   cd lambda/build
   zip -r ../lambda_function.zip .
   cd ..
   ```
   
## Deployment Options
**Option 1: Manual Upload via AWS Console**
1. Go to AWS Lambda Console → Create function
2. Choose "Author from scratch"
3. Set:
    - Runtime: Python 3.11
    - Handler: handler.lambda_handler
4. Upload lambda_function.zip
5. Set environment variables or include .env manually
6. Attach the appropriate IAM role
7. Save and test your function

**Option 2: Deploy via AWS CLI**
```
aws lambda create-function --function-name MyMySQLToS3Export \
--zip-file fileb://lambda_function.zip \
--handler handler.lambda_handler \
--runtime python3.11 \
--role arn:aws:iam::your-account-id:role/your-lambda-role
   ```

## Local Testing (Optional)
If you want to test the logic locally before deployment:
```
  python main.py
```
Or simulate Lambda locally: (This will run export_to_parquet() immediately)
```
cd lambda
python handler.py
```

## Security Notes
- Avoid committing .env to version control
- Consider using AWS Secrets Manager for credentials in production
- Do not include unnecessary files (e.g. virtual environments) in the zip

## .gitignore Suggestions
```
lambda/build/
lambda/lambda_function.zip
```

## Contributions
Pull requests are welcome! Open an issue first if you'd like to suggest a new feature or enhancement for Lambda support.
