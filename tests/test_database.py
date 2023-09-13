import pytest
from unittest.mock import patch

from botocore.exceptions import ClientError

from wells.database import record_to_db

image1 = open('tests/images/1.tiff', 'rb').read()

@patch('wells.database.dynamodb.Table')
@patch('wells.database.hash_log')
def test_put_item_calls(mock_hash_log, mock_table):
    record_to_db(image1, 'bucket', 'key')
    assert mock_hash_log.called
    assert mock_table.return_value.put_item.called

@patch('wells.database.dynamodb.Table')
@patch('wells.database.hash_log', return_value="hashvalue")
def test_put_item_call_args(mock_hash_log, mock_table):
    record_to_db(image1, 'bucket', 'key')
    mock_hash_log.assert_called_with(image1)
    mock_table.return_value.put_item.assert_called_with(
        Item={"Id": "hashvalue", "Bucket": "bucket", "S3Key": "key"},
        ConditionExpression="attribute_not_exists(Id)")

@patch('wells.database.print')
@patch('wells.database.dynamodb.Table')
@patch('wells.database.hash_log')
def test_put_item_output(mock_hash_log, mock_table, mock_print):
    record_to_db(image1, 'bucket', 'key')
    mock_print.assert_called_with('Added well log data to the database')

@patch('wells.database.print')
@patch('wells.database.dynamodb.Table')
@patch('wells.database.hash_log')
def test_put_item_duplicate(mock_hash_log, mock_table, mock_print):
    error = ClientError(error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
                        operation_name="operation_name")
    mock_table.return_value.put_item.side_effect = error
    record_to_db(image1, 'bucket', 'key')
    mock_print.assert_called_with('TIFF file already exists!')

@patch('wells.database.dynamodb.Table')
@patch('wells.database.hash_log')
def test_put_item_other_error(mock_hash_log, mock_table):
    error = ClientError(error_response={"Error": {"Code": "AnotherCode"}},
                        operation_name="operation_name")
    mock_table.return_value.put_item.side_effect = error
    with pytest.raises(ClientError):
        record_to_db(image1, 'bucket', 'key')

@pytest.mark.integration
@patch('wells.database.print')
@patch('wells.database.dynamodb.Table')
def test_put_item_integration(mock_table, mock_print):
    record_to_db(image1, 'bucket', 'key')
    mock_print.assert_called_with('Added well log data to the database')
