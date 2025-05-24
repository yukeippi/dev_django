# EC2デプロイガイド

このガイドでは、DjangoアプリケーションをEC2サーバーにデプロイする手順を説明します。

## 前提条件

- Ubuntu 22.04 LTS のEC2インスタンス
- SSH接続可能な状態
- ドメイン名（オプション）

## 1. EC2インスタンスの初期設定

### 1.1 サーバーにSSH接続

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 1.2 初期設定スクリプトの実行

```bash
# リポジトリをクローン（一時的）
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git temp_repo
cd temp_repo

# 初期設定スクリプトを実行
chmod +x deploy/server_setup.sh
./deploy/server_setup.sh
```

### 1.3 SSH鍵の設定

スクリプト実行後に表示される公開鍵をコピーして、GitHubリポジトリの設定に追加します：

1. GitHubリポジトリページで `Settings` → `Deploy keys` に移動
2. `Add deploy key` をクリック
3. 表示された公開鍵を貼り付け
4. `Allow write access` にチェック（必要に応じて）
5. `Add key` をクリック

## 2. 環境変数の設定

### 2.1 .envファイルの編集

```bash
sudo -u www-data nano /var/www/diary/.env
```

以下の値を適切に設定してください：

```env
# Django設定
SECRET_KEY=your_very_secure_secret_key_here
DJANGO_SETTINGS_MODULE=config.settings_production

# データベース設定
POSTGRES_DB=diary_production
POSTGRES_USER=diary_user
POSTGRES_PASSWORD=your_secure_database_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# サーバー設定
DOMAIN_NAME=your-domain.com
SERVER_IP=your_ec2_public_ip

# HTTPS設定（SSL証明書使用時）
USE_HTTPS=False
```

### 2.2 PostgreSQLパスワードの更新

```bash
sudo -u postgres psql
ALTER USER diary_user WITH PASSWORD 'your_secure_database_password';
\q
```

## 3. 初回デプロイ

### 3.1 デプロイスクリプトの編集

```bash
sudo nano /var/www/diary/deploy/deploy.sh
```

`REPO_URL` を実際のリポジトリURLに変更：

```bash
REPO_URL="git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git"
```

### 3.2 デプロイの実行

```bash
cd /var/www/diary
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 4. GitHub Actions の設定

### 4.1 GitHub Secrets の設定

GitHubリポジトリの `Settings` → `Secrets and variables` → `Actions` で以下のシークレットを追加：

- `EC2_HOST`: EC2インスタンスのパブリックIP
- `EC2_USERNAME`: `ubuntu`
- `EC2_SSH_KEY`: EC2接続用の秘密鍵の内容

### 4.2 自動デプロイの確認

mainブランチにpushすると、自動的にテストとデプロイが実行されます。

## 5. SSL証明書の設定（オプション）

### 5.1 Let's Encryptを使用

```bash
# SSL証明書の取得
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自動更新の設定
sudo crontab -e
# 以下の行を追加
0 12 * * * /usr/bin/certbot renew --quiet
```

### 5.2 HTTPS設定の有効化

```bash
# .envファイルを編集
sudo -u www-data nano /var/www/diary/.env
```

`USE_HTTPS=True` に変更し、サービスを再起動：

```bash
sudo systemctl restart diary-gunicorn
sudo systemctl restart nginx
```

## 6. 運用・監視

### 6.1 ログの確認

```bash
# Gunicornログ
sudo journalctl -u diary-gunicorn -f

# Nginxエラーログ
sudo tail -f /var/log/nginx/diary_error.log

# Djangoアプリケーションログ
sudo tail -f /var/log/diary/django.log
```

### 6.2 サービスの状態確認

```bash
# サービス状態の確認
sudo systemctl status diary-gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql

# サービスの再起動
sudo systemctl restart diary-gunicorn
sudo systemctl restart nginx
```

### 6.3 データベースのバックアップ

```bash
# バックアップの作成
sudo -u postgres pg_dump diary_production > backup_$(date +%Y%m%d_%H%M%S).sql

# 定期バックアップの設定（crontab）
sudo crontab -e
# 毎日午前2時にバックアップ
0 2 * * * sudo -u postgres pg_dump diary_production > /var/backups/diary_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

## 7. トラブルシューティング

### 7.1 よくある問題

1. **502 Bad Gateway エラー**
   - Gunicornサービスが起動していない
   - `sudo systemctl start diary-gunicorn`

2. **静的ファイルが表示されない**
   - 静的ファイルの収集を実行
   - `sudo -u www-data venv/bin/python manage.py collectstatic`

3. **データベース接続エラー**
   - PostgreSQLサービスの確認
   - `sudo systemctl status postgresql`
   - 認証情報の確認

### 7.2 パフォーマンス最適化

```bash
# Nginxの設定調整
sudo nano /etc/nginx/nginx.conf

# worker_processes を CPU コア数に設定
worker_processes auto;

# worker_connections を調整
events {
    worker_connections 1024;
}
```

## 8. セキュリティ対策

### 8.1 定期的なアップデート

```bash
# システムアップデート
sudo apt update && sudo apt upgrade -y

# Pythonパッケージのアップデート
cd /var/www/diary
sudo -u www-data venv/bin/poetry update
```

### 8.2 ファイアウォール設定の確認

```bash
# UFW状態確認
sudo ufw status

# 必要に応じてルールを追加
sudo ufw allow from specific_ip to any port 22
```

このガイドに従って設定することで、安全で効率的なDjangoアプリケーションのデプロイが可能になります。
