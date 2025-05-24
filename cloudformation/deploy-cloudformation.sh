#!/bin/bash

# CloudFormation ECS Fargateデプロイメントスクリプト
set -e

# 設定変数
AWS_REGION=${AWS_REGION:-"ap-northeast-1"}
PROJECT_NAME=${PROJECT_NAME:-"diary-app"}
STACK_PREFIX=${STACK_PREFIX:-"diary-app"}

echo "=== CloudFormation ECS Fargateデプロイメント開始 ==="

# パラメータファイルの存在確認
if [ ! -f "parameters.json" ]; then
    echo "エラー: parameters.jsonファイルが見つかりません"
    echo "parameters.jsonファイルを作成して、必要なパラメータを設定してください"
    exit 1
fi

# パラメータファイルの検証
if grep -q "CHANGE_THIS" parameters.json; then
    echo "エラー: parameters.jsonファイル内にデフォルト値が残っています"
    echo "RDSPasswordとDjangoSecretKeyを適切な値に変更してください"
    exit 1
fi

echo "1. メインインフラストラクチャ（VPC、サブネット）をデプロイ中..."
aws cloudformation deploy \
    --template-file main.yaml \
    --stack-name ${STACK_PREFIX}-main \
    --parameter-overrides file://parameters.json \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION \
    --no-fail-on-empty-changeset

echo "2. セキュリティグループとRDSをデプロイ中..."
aws cloudformation deploy \
    --template-file security-rds.yaml \
    --stack-name ${STACK_PREFIX}-security-rds \
    --parameter-overrides ProjectName=$PROJECT_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION \
    --no-fail-on-empty-changeset

echo "3. ALBとSSMパラメータをデプロイ中..."
aws cloudformation deploy \
    --template-file alb-ssm.yaml \
    --stack-name ${STACK_PREFIX}-alb-ssm \
    --parameter-overrides ProjectName=$PROJECT_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION \
    --no-fail-on-empty-changeset

echo "4. ECSとECRをデプロイ中..."
aws cloudformation deploy \
    --template-file ecs.yaml \
    --stack-name ${STACK_PREFIX}-ecs \
    --parameter-overrides ProjectName=$PROJECT_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION \
    --no-fail-on-empty-changeset

echo "=== インフラストラクチャデプロイ完了 ==="

# ECRリポジトリURLを取得
ECR_REPOSITORY_URI=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_PREFIX}-ecs \
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "ECRリポジトリURI: $ECR_REPOSITORY_URI"

# アプリケーションURLを取得
APPLICATION_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_PREFIX}-alb-ssm \
    --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "アプリケーションURL: $APPLICATION_URL"

echo ""
echo "=== 次のステップ ==="
echo "1. Dockerイメージをビルドしてプッシュ:"
echo "   cd .."
echo "   export AWS_ACCOUNT_ID=\$(aws sts get-caller-identity --query Account --output text)"
echo "   export ECR_REPOSITORY_URI=$ECR_REPOSITORY_URI"
echo "   ./deploy.sh"
echo ""
echo "2. データベースマイグレーション:"
echo "   ECS_CLUSTER=\$(aws cloudformation describe-stacks --stack-name ${STACK_PREFIX}-ecs --query 'Stacks[0].Outputs[?OutputKey==\`ECSClusterName\`].OutputValue' --output text)"
echo "   # マイグレーションタスクを実行（詳細はDEPLOYMENT.mdを参照）"
echo ""
echo "3. アプリケーションにアクセス:"
echo "   $APPLICATION_URL"
