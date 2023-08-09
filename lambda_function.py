"""
AWS Lambda handler
"""
from hashlib import md5

import boto3
from botocore.exceptions import ClientError

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

    record_to_db(obj, bucket, key)


def record_to_db(obj, bucket, key):
    hash_val = hash_log(obj)

    table = dynamodb.Table("WellLogs")
    item = {
        "Id": hash_val,
        "Bucket": bucket,
        "S3Key": key,
    }

    try:
        table.put_item(Item=item)
        print(f"Added TIFF to {bucket}")
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print("TIFF file already exists!")
        else:
            raise error
    except Exception as error:
        raise error


def hash_log(byte_string):
    hash_val = md5(byte_string)

    return hash_val.hexdigest()


def main(file_path):
    with open(sys.argv[1], "rb") as f:
        hash_val = hash_log(f.read())

    return hash_val


if __name__ == "__main__":
    import sys

    print(main(sys.argv[1]))
