#!/bin/bash

# デプロイスクリプト
# GitHubからコードを取得してアプリケーションをデプロイ

set -e

# 設定
REPO_URL="git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git"  # GitHubリポジトリのURL
APP_DIR="/var/www/diary"
BRANCH="main"  # デプロイするブランチ

echo "=== デプロイを開始します ==="

# アプリケーションディレクトリに移動
cd $APP_DIR

# Gitリポジトリのクローンまたは更新
if [ ! -d ".git" ]; then
    echo "リポジトリをクローンしています..."
    sudo -u www-data git clone $REPO_URL .
else
    echo "リポジトリを更新しています..."
    sudo -u www-data git fetch origin
    sudo -u www-data git reset --hard origin/$BRANCH
fi

# 仮想環境の作成・更新
echo "仮想環境を設定しています..."
if [ ! -d "venv" ]; then
    sudo -u www-data python3 -m venv venv
fi

# 依存関係のインストール
echo "依存関係をインストールしています..."
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install poetry
sudo -u www-data venv/bin/poetry install --only=main

# 環境変数ファイルの確認
if [ ! -f ".env" ]; then
    echo "警告: .envファイルが見つかりません。作成してください。"
    echo "テンプレートを作成します..."
    sudo -u www-data cat > .env << EOF
# Django設定
SECRET_KEY=your_secret_key_here
DJANGO_SETTINGS_MODULE=config.settings_production

# データベース設定
POSTGRES_DB=diary_production
POSTGRES_USER=diary_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# サーバー設定
DOMAIN_NAME=your-domain.com
SERVER_IP=your_server_ip

# HTTPS設定（SSL証明書使用時）
USE_HTTPS=False

# Redis設定（使用する場合）
# REDIS_URL=redis://localhost:6379/0
EOF
    echo ".envファイルを編集して正しい値を設定してください。"
    exit 1
fi

# データベースマイグレーション
echo "データベースマイグレーションを実行しています..."
sudo -u www-data venv/bin/python manage.py migrate

# 静的ファイルの収集
echo "静的ファイルを収集しています..."
sudo -u www-data venv/bin/python manage.py collectstatic --noinput

# Nginxの設定をコピー
echo "Nginxの設定を更新しています..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/diary
sudo ln -sf /etc/nginx/sites-available/diary /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginxの設定をテスト
sudo nginx -t

# systemdサービスファイルをコピー
echo "systemdサービスを設定しています..."
sudo cp deploy/systemd/diary-gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload

# サービスの再起動
echo "サービスを再起動しています..."
sudo systemctl restart diary-gunicorn
sudo systemctl enable diary-gunicorn
sudo systemctl restart nginx

# サービスの状態確認
echo "サービスの状態を確認しています..."
sudo systemctl status diary-gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo "=== デプロイが完了しました ==="
echo "アプリケーションは以下のURLでアクセスできます："
echo "http://$(curl -s ifconfig.me)"
echo ""
echo "ログの確認："
echo "  Gunicorn: sudo journalctl -u diary-gunicorn -f"
echo "  Nginx: sudo tail -f /var/log/nginx/diary_error.log"
echo "  Django: sudo tail -f /var/log/diary/django.log"
