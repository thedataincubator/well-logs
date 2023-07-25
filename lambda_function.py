"""
AWS Lambda handler
"""
from hashlib import md5

from io import BytesIO

from botocore.exceptions import ClientError
import boto3
from imagehash import average_hash
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("WellLogs")


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

    image = Image.open(BytesIO(obj))
    hash_val = str(average_hash(image))

    item = {
        "Id": hash_val,
        "Bucket": bucket,
        "S3Key": key,
    }

    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(Id)"
        )
        print("Added well log data to the database")
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print("TIFF file already exists!")
        else:
            raise error
    except Exception as error:
        raise error
