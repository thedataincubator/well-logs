#!/bin/bash
set -eu

source configs/config
source bin/usage.sh

create() {
  aws s3api create-bucket --bucket "$SOURCE_BUCKET" --region us-east-1
}

delete() {
  aws s3 rm s3://"$SOURCE_BUCKET" --recursive --exclude "*" --include "*.tif"
}


main "$@"
