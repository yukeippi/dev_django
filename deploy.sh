#!/bin/bash

# ECS Fargateデプロイメントスクリプト（CloudFormation版）
set -e

# 設定変数
AWS_REGION=${AWS_REGION:-"ap-northeast-1"}
PROJECT_NAME=${PROJECT_NAME:-"diary-app"}
STACK_PREFIX=${STACK_PREFIX:-"diary-app"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

# AWS Account IDを自動取得
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "エラー: AWS Account IDを取得できませんでした"
    echo "AWS CLIが正しく設定されているか確認してください"
    exit 1
fi

# ECRリポジトリURIを取得
if [ -z "$ECR_REPOSITORY_URI" ]; then
    ECR_REPOSITORY_URI=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_PREFIX}-ecs \
        --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
        --output text \
        --region $AWS_REGION 2>/dev/null)
    
    if [ -z "$ECR_REPOSITORY_URI" ]; then
        echo "エラー: ECRリポジトリURIを取得できませんでした"
        echo "CloudFormationスタックが正しくデプロイされているか確認してください"
        exit 1
    fi
fi

# ECSクラスター名とサービス名を取得
ECS_CLUSTER=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_PREFIX}-ecs \
    --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
    --output text \
    --region $AWS_REGION)

ECS_SERVICE=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_PREFIX}-ecs \
    --query 'Stacks[0].Outputs[?OutputKey==`ECSServiceName`].OutputValue' \
    --output text \
    --region $AWS_REGION)

ECR_REPOSITORY=$(echo $ECR_REPOSITORY_URI | cut -d'/' -f2)

echo "=== ECS Fargateデプロイメント開始 ==="

# 1. ECRにログイン
echo "ECRにログイン中..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Dockerイメージをビルド
echo "Dockerイメージをビルド中..."
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

# 3. イメージにタグを付ける
echo "イメージにタグを付与中..."
docker tag $ECR_REPOSITORY:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# 4. ECRにプッシュ
echo "ECRにイメージをプッシュ中..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# 5. タスク定義を更新
echo "タスク定義を更新中..."
# タスク定義ファイルのプレースホルダーを置換
sed -e "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" \
    -e "s/YOUR_REGION/$AWS_REGION/g" \
    ecs-task-definition.json > ecs-task-definition-updated.json

# 6. タスク定義を登録
echo "新しいタスク定義を登録中..."
aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition-updated.json \
    --region $AWS_REGION

# 7. サービスを更新
echo "ECSサービスを更新中..."
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --force-new-deployment \
    --region $AWS_REGION

# 8. デプロイメント完了を待機
echo "デプロイメント完了を待機中..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE \
    --region $AWS_REGION

echo "=== デプロイメント完了 ==="

# 一時ファイルを削除
rm -f ecs-task-definition-updated.json

echo "アプリケーションが正常にデプロイされました！"
