from botocore.exceptions import ClientError
import boto3

from wells.hash_log import hash_log

dynamodb = boto3.resource("dynamodb")


def record_to_db(obj, bucket, key):
    hash_val = hash_log(obj)

    table = dynamodb.Table("WellLogs")
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
