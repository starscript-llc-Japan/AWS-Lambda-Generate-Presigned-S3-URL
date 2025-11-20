# Lambda S3 Presigned URL Generator

This project demonstrates an AWS Lambda function that generates a presigned URL for an S3 object. The URL allows temporary access to download a file (valid for 24 hours).

## Project Structure

```text
project-root/
├─ README.md
├─ lambda/
│ ├─ generate_download_url.py # Lambda function
│ └─ requirements.txt # Dependencies (boto3, etc.)
├─ .gitignore
└─ LICENSE

## Usage

1. Deploy the Lambda function in AWS.
2. Ensure the Lambda execution role has permission to `s3:GetObject`.
3. Invoke the Lambda function via AWS Console or API Gateway.
4. The function returns a JSON containing the `presigned download_url`.
5. Open the URL in a browser or use it in your application to download the file.

## Notes

- URL validity is set to 24 hours.
- You can customize the bucket name and file key in `generate_download_url.py`.