#!/bin/sh -e

export AWS_ACCESS_KEY_ID=AKIAJGVM2O23IDRVLK3A
export AWS_SECRET_ACCESS_KEY=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
export AWS_DEFAULT_REGION=us-east-1

role_name="AWSLambdaExecutionRole"
policy_arn="arn:aws:iam::aws:policy/AWSLambdaFullAccess"
lambda_function_name="alexafindmyiphone"
timeout=300
memory_size=128

build_prefix="$PWD/build"
aws_prefix="$PWD/aws"
src_prefix="$PWD/src"

aws_trust_policy="$aws_prefix/TrustPolicy.json"

get_release_filename() {
  version="$(cat $src_prefix/service.py | grep 'version' | grep -o '\d.\d')"
  echo "$build_prefix/$lambda_function_name-$version.zip"
}

build_lambda_function_for_release() {
  mkdir -p "$build_prefix"
  cd $src_prefix
  zip -r "$(get_release_filename)" . -x "*.DS_Store"
}

create_iam_role() {
  aws iam create-role \
    --role-name $role_name \
    --assume-role-policy-document "file://$aws_trust_policy" \
    --description "Allows Lambda functions to call AWS services on your behalf."

  aws iam attach-role-policy \
    --role-name $role_name \
    --policy-arn "$policy_arn"
  sleep 5
}

get_role_arn() {
  aws iam get-role --role-name $role_name --query 'Role.Arn' --output text
}

create_lambda_function() {
  aws lambda create-function \
    --function-name $lambda_function_name \
    --runtime python3.6 \
    --role "$(get_role_arn)" \
    --handler "service.handler" \
    --zip-file fileb://"$(get_release_filename)" \
    --description "Amazon Echo handler to trigger native Apple Find My iPhone" \
    --timeout $timeout \
    --memory-size $memory_size
}

setup() {
  build_lambda_function_for_release
  create_iam_role
  create_lambda_function
}

setup
