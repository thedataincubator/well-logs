<<<<<<< HEAD
"""
AWS Lambda handler
"""
from hashlib import md5

from io import BytesIO

from botocore.exceptions import ClientError
=======
>>>>>>> 5ba8c2c (Restructure project as a Python package)
import boto3

from wells.database import record_to_db

s3 = boto3.client("s3")


def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
        raise e
    else:
        obj = response["Body"].read()

    record_to_db(obj, bucket, key)
