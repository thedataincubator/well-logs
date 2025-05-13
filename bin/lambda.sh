#!/bin/bash
set -eu

source configs/config
set +e
source bin/usage.sh

role_name="$FUNCTION_NAME"Role

parse_json() {
  region="$(aws configure get region)"
  account_number="$(aws sts get-caller-identity | jq -r ".Account")"
  arn="arn:aws:lambda:$region:$account_number:function:$FUNCTION_NAME"
  filter=".LambdaFunctionConfigurations[0].LambdaFunctionArn = \"$arn\""

  jq "$filter" configs/notification.json
}

package_deployment() {
  rm -rf package deployment.zip
  mkdir package
  PIP_REQUIRE_VIRTUALENV=false pip install \
	  --platform manylinux2014_x86_64 \
	  --target=package \
	  --implementation cp \
	  --python-version 3.10 \
	  --only-binary=:all: \
	  .
  rm -rf package/scipy*
  (cd package && zip -r ../deployment.zip .)
  zip deployment.zip lambda_function.py
  aws s3 cp deployment.zip s3://"$SOURCE_BUCKET"/deployment.zip
}

create() {
  echo "Creating Lambda function $FUNCTION_NAME"

  echo "Setting up policies and roles"
  aws iam create-role --role-name "$role_name" --assume-role-policy-document file://configs/trust-policy.json
  aws iam attach-role-policy --role-name "$role_name" --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
  aws iam attach-role-policy --role-name "$role_name" --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
  aws iam attach-role-policy --role-name "$role_name" --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
  sleep 5

  echo "Packing the deployment"
  account_number="$(aws sts get-caller-identity | jq -r ".Account")"
  package_deployment

  aws lambda create-function \
	  --function-name "$FUNCTION_NAME" \
	  --runtime python3.10 \
	  --code S3Bucket="$SOURCE_BUCKET",S3Key=deployment.zip \
	  --handler lambda_function.lambda_handler \
	  --role arn:aws:iam::"$account_number":role/"$role_name" \
	  --timeout 30 \
	  --memory-size 1024

  aws lambda add-permission \
	  --function-name "$FUNCTION_NAME" \
	  --principal s3.amazonaws.com \
	  --statement-id s3invoke \
	  --action "lambda:InvokeFunction" \
	  --source-arn arn:aws:s3:::"$SOURCE_BUCKET" \
	  --source-account "$account_number"

  aws s3api put-bucket-notification-configuration \
	  --bucket "$SOURCE_BUCKET" \
	  --notification-configuration "$(parse_json)"
}

delete() {
  echo "Deleting Lamdba function $FUNCTION_NAME"

  aws lambda delete-function --function-name "$FUNCTION_NAME"

  aws iam detach-role-policy --role-name "$role_name" --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
  aws iam detach-role-policy --role-name "$role_name" --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
  aws iam detach-role-policy --role-name "$role_name" --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess

  aws iam delete-role --role-name "$role_name"
}


main "$@"
