#!/bin/bash

# EC2サーバー初期設定スクリプト
# Ubuntu 22.04 LTS用

set -e

echo "=== EC2サーバーの初期設定を開始します ==="

# システムアップデート
echo "システムをアップデートしています..."
sudo apt update && sudo apt upgrade -y

# 必要なパッケージのインストール
echo "必要なパッケージをインストールしています..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql \
    postgresql-contrib \
    git \
    curl \
    ufw \
    certbot \
    python3-certbot-nginx

# PostgreSQLの設定
echo "PostgreSQLを設定しています..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# データベースとユーザーの作成
echo "データベースとユーザーを作成しています..."
sudo -u postgres psql << EOF
CREATE DATABASE diary_production;
CREATE USER diary_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE diary_user SET client_encoding TO 'utf8';
ALTER ROLE diary_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE diary_user SET timezone TO 'Asia/Tokyo';
GRANT ALL PRIVILEGES ON DATABASE diary_production TO diary_user;
\q
EOF

# アプリケーション用ディレクトリの作成
echo "アプリケーション用ディレクトリを作成しています..."
sudo mkdir -p /var/www/diary
sudo mkdir -p /var/log/diary
sudo mkdir -p /var/www/diary/static
sudo mkdir -p /var/www/diary/media

# www-dataユーザーに権限を付与
sudo chown -R www-data:www-data /var/www/diary
sudo chown -R www-data:www-data /var/log/diary

# Nginxの設定
echo "Nginxを設定しています..."
sudo systemctl start nginx
sudo systemctl enable nginx

# ファイアウォールの設定
echo "ファイアウォールを設定しています..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Git設定（デプロイ用）
echo "Git設定を行っています..."
sudo -u www-data ssh-keygen -t rsa -b 4096 -f /var/www/.ssh/id_rsa -N ""
echo "以下の公開鍵をGitHubのDeploy Keysに追加してください："
sudo -u www-data cat /var/www/.ssh/id_rsa.pub

echo "=== 初期設定が完了しました ==="
echo "次のステップ："
echo "1. GitHubにDeploy Keyを追加"
echo "2. 環境変数ファイル(.env)を作成"
echo "3. デプロイスクリプトを実行"
