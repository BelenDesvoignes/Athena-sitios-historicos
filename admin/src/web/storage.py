import boto3
from flask import current_app


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=current_app.config["STORAGE_ENDPOINT_URL"],
        aws_access_key_id=current_app.config["MINIO_ACCESS_KEY"],
        aws_secret_access_key=current_app.config["MINIO_SECRET_KEY"],
        region_name='us-east-1',
    )
