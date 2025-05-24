# ECS Fargate デプロイメント手順（CloudFormation版）

このドキュメントでは、DjangoアプリケーションをAWS ECS FargateにCloudFormationを使用してデプロイする手順を説明します。

## 前提条件

- AWS CLI がインストールされ、設定されていること
- Docker がインストールされていること
- 適切なAWS権限を持つIAMユーザーまたはロールが設定されていること

## 1. 初期設定

### 1.1 CloudFormationパラメータファイルの設定

```bash
cd cloudformation
cp parameters.json parameters-local.json
```

`parameters-local.json` ファイルを編集して、以下の値を設定してください：

- `RDSPassword`: RDSデータベースのパスワード（8文字以上）
- `DjangoSecretKey`: DjangoのSECRET_KEY（50文字以上）
- その他必要に応じて設定値を調整

### 1.2 Django SECRET_KEYの生成

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 1.3 強力なパスワードの生成

```bash
openssl rand -base64 32
```

## 2. インフラストラクチャのデプロイ

### 2.1 CloudFormationスタックのデプロイ

```bash
cd cloudformation
# パラメータファイル名を指定してデプロイ
cp parameters-local.json parameters.json
./deploy-cloudformation.sh
```

実行後、以下の情報が出力されます：
- ECRリポジトリURI
- アプリケーションURL

## 3. アプリケーションのデプロイ

### 3.1 環境変数の設定

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=ap-northeast-1
```

### 3.2 デプロイスクリプトの実行

```bash
chmod +x deploy.sh
./deploy.sh
```

## 4. データベースの初期化

### 4.1 ECSタスクでマイグレーションを実行

```bash
# CloudFormationスタックから必要な情報を取得
STACK_PREFIX="diary-app"
AWS_REGION="ap-northeast-1"

ECS_CLUSTER=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-ecs \
  --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
  --output text \
  --region $AWS_REGION)

PRIVATE_SUBNET_1=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-main \
  --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet1Id`].OutputValue' \
  --output text \
  --region $AWS_REGION)

PRIVATE_SUBNET_2=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-main \
  --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet2Id`].OutputValue' \
  --output text \
  --region $AWS_REGION)

ECS_SECURITY_GROUP=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-security-rds \
  --query 'Stacks[0].Outputs[?OutputKey==`ECSSecurityGroupId`].OutputValue' \
  --output text \
  --region $AWS_REGION)

# マイグレーション用のタスクを実行
aws ecs run-task \
  --cluster $ECS_CLUSTER \
  --task-definition diary-app \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [
      {
        "name": "diary-app",
        "command": ["python", "manage.py", "migrate"]
      }
    ]
  }' \
  --region $AWS_REGION
```

### 4.2 スーパーユーザーの作成

```bash
aws ecs run-task \
  --cluster $ECS_CLUSTER \
  --task-definition diary-app \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [
      {
        "name": "diary-app",
        "command": ["python", "manage.py", "createsuperuser", "--noinput"],
        "environment": [
          {"name": "DJANGO_SUPERUSER_USERNAME", "value": "admin"},
          {"name": "DJANGO_SUPERUSER_EMAIL", "value": "admin@example.com"},
          {"name": "DJANGO_SUPERUSER_PASSWORD", "value": "your-admin-password"}
        ]
      }
    ]
  }' \
  --region $AWS_REGION
```

## 5. アプリケーションの確認

### 5.1 アプリケーションURLの取得

```bash
cd cloudformation
aws cloudformation describe-stacks \
  --stack-name diary-app-alb-ssm \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text
```

### 5.2 ヘルスチェック

ブラウザで以下のURLにアクセスして、アプリケーションが正常に動作していることを確認してください：

- `http://<ALB_DNS_NAME>/admin/` - Django管理画面
- `http://<ALB_DNS_NAME>/` - アプリケーションのトップページ

## 6. 継続的デプロイメント

アプリケーションコードを更新した場合は、以下のコマンドでデプロイできます：

```bash
./deploy.sh
```

## 7. モニタリング

### 7.1 CloudWatchログの確認

```bash
aws logs describe-log-groups --log-group-name-prefix "/ecs/diary-app"
```

### 7.2 ECSサービスの状態確認

```bash
aws ecs describe-services --cluster diary-app-cluster --services diary-app-service
```

## 8. トラブルシューティング

### 8.1 タスクが起動しない場合

```bash
# タスクの詳細を確認
aws ecs describe-tasks --cluster diary-app-cluster --tasks <task-arn>

# ログを確認
aws logs get-log-events --log-group-name "/ecs/diary-app" --log-stream-name "ecs/diary-app/<task-id>"
```

### 8.2 データベース接続エラー

- RDSセキュリティグループの設定を確認
- SSMパラメータの値を確認
- VPCとサブネットの設定を確認

## 9. リソースの削除

テスト環境を削除する場合：

```bash
cd cloudformation
STACK_PREFIX="diary-app"
AWS_REGION="ap-northeast-1"

# スタックを逆順で削除
aws cloudformation delete-stack --stack-name ${STACK_PREFIX}-ecs --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name ${STACK_PREFIX}-ecs --region $AWS_REGION

aws cloudformation delete-stack --stack-name ${STACK_PREFIX}-alb-ssm --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name ${STACK_PREFIX}-alb-ssm --region $AWS_REGION

aws cloudformation delete-stack --stack-name ${STACK_PREFIX}-security-rds --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name ${STACK_PREFIX}-security-rds --region $AWS_REGION

aws cloudformation delete-stack --stack-name ${STACK_PREFIX}-main --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name ${STACK_PREFIX}-main --region $AWS_REGION

echo "すべてのCloudFormationスタックが削除されました"
```

## セキュリティ考慮事項

- RDSパスワードとDjango SECRET_KEYは安全に管理してください
- 本番環境では、より強力なインスタンスタイプを使用してください
- HTTPS証明書を設定して、SSL/TLSを有効にしてください
- セキュリティグループのルールを最小限に制限してください

## コスト最適化

- 開発環境では、ECSタスク数を1に設定してください
- 使用しない時間帯はECSサービスのタスク数を0に設定してください
- RDSインスタンスのサイズを適切に調整してください
