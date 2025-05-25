#!/bin/bash

# ロールバック対応デプロイシステムのセットアップスクリプト
# 既存のサーバーを新しいデプロイシステムに移行します

set -e

# 設定
APP_NAME="diary"
BASE_DIR="/var/www"
OLD_APP_DIR="/var/www/diary"
RELEASES_DIR="$BASE_DIR/releases"
SHARED_DIR="$BASE_DIR/shared"
SCRIPTS_DIR="$BASE_DIR/scripts"
CURRENT_LINK="$BASE_DIR/$APP_NAME"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SETUP: $1"
}

# エラーハンドリング
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 権限確認
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        error_exit "このスクリプトはroot権限で実行してください"
    fi
}

# 既存システムのバックアップ
backup_existing_system() {
    log "既存システムのバックアップを作成しています..."
    
    local backup_dir="/var/backups/diary-migration-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    if [ -d "$OLD_APP_DIR" ]; then
        log "既存のアプリケーションディレクトリをバックアップ: $backup_dir"
        cp -r "$OLD_APP_DIR" "$backup_dir/"
        
        # .envファイルも個別にバックアップ
        if [ -f "$OLD_APP_DIR/.env" ]; then
            cp "$OLD_APP_DIR/.env" "$backup_dir/env-backup"
        fi
    fi
    
    log "✅ バックアップが完了しました: $backup_dir"
}

# 新しいディレクトリ構造の作成
setup_directory_structure() {
    log "新しいディレクトリ構造を作成しています..."
    
    # ディレクトリ作成
    mkdir -p "$RELEASES_DIR"
    mkdir -p "$SHARED_DIR"
    mkdir -p "$SCRIPTS_DIR"
    
    # 共有ディレクトリの作成
    mkdir -p "$SHARED_DIR/logs"
    mkdir -p "$SHARED_DIR/media"
    mkdir -p "$SHARED_DIR/static"
    
    # 権限設定
    chown -R www-data:www-data "$BASE_DIR"
    
    log "✅ ディレクトリ構造が作成されました"
}

# 既存の.envファイルを移行
migrate_env_file() {
    log ".envファイルを移行しています..."
    
    if [ -f "$OLD_APP_DIR/.env" ]; then
        cp "$OLD_APP_DIR/.env" "$SHARED_DIR/.env"
        chown www-data:www-data "$SHARED_DIR/.env"
        log "✅ .envファイルを移行しました"
    else
        log "⚠️  既存の.envファイルが見つかりません。テンプレートを作成します..."
        cat > "$SHARED_DIR/.env" << 'EOF'
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
EOF
        chown www-data:www-data "$SHARED_DIR/.env"
        log "⚠️  $SHARED_DIR/.env ファイルを編集して正しい値を設定してください"
    fi
}

# 既存のメディアファイルを移行
migrate_media_files() {
    log "メディアファイルを移行しています..."
    
    if [ -d "$OLD_APP_DIR/media" ] && [ "$(ls -A $OLD_APP_DIR/media)" ]; then
        cp -r "$OLD_APP_DIR/media/"* "$SHARED_DIR/media/"
        chown -R www-data:www-data "$SHARED_DIR/media"
        log "✅ メディアファイルを移行しました"
    else
        log "移行するメディアファイルがありません"
    fi
}

# 既存のログファイルを移行
migrate_log_files() {
    log "ログファイルを移行しています..."
    
    if [ -d "$OLD_APP_DIR/logs" ] && [ "$(ls -A $OLD_APP_DIR/logs)" ]; then
        cp -r "$OLD_APP_DIR/logs/"* "$SHARED_DIR/logs/"
        chown -R www-data:www-data "$SHARED_DIR/logs"
        log "✅ ログファイルを移行しました"
    else
        log "移行するログファイルがありません"
    fi
}

# スクリプトファイルのコピー
copy_scripts() {
    log "デプロイスクリプトをコピーしています..."
    
    # 現在のディレクトリからスクリプトをコピー
    local script_source_dir="$(dirname "$0")"
    
    if [ -f "$script_source_dir/deploy-with-rollback.sh" ]; then
        cp "$script_source_dir/deploy-with-rollback.sh" "$SCRIPTS_DIR/"
        chmod +x "$SCRIPTS_DIR/deploy-with-rollback.sh"
        log "✅ deploy-with-rollback.sh をコピーしました"
    else
        error_exit "deploy-with-rollback.sh が見つかりません"
    fi
    
    if [ -f "$script_source_dir/health-check.sh" ]; then
        cp "$script_source_dir/health-check.sh" "$SCRIPTS_DIR/"
        chmod +x "$SCRIPTS_DIR/health-check.sh"
        log "✅ health-check.sh をコピーしました"
    else
        error_exit "health-check.sh が見つかりません"
    fi
    
    chown -R www-data:www-data "$SCRIPTS_DIR"
}

# 既存アプリケーションを最初のリリースとして移行
migrate_current_app() {
    log "既存のアプリケーションを最初のリリースとして移行しています..."
    
    if [ ! -d "$OLD_APP_DIR" ]; then
        log "⚠️  既存のアプリケーションディレクトリが見つかりません"
        return 0
    fi
    
    local initial_version="legacy-$(date +%Y%m%d-%H%M%S)"
    local release_dir="$RELEASES_DIR/$initial_version"
    
    # 既存のアプリケーションをコピー
    cp -r "$OLD_APP_DIR" "$release_dir"
    chown -R www-data:www-data "$release_dir"
    
    # 共有ファイルのシンボリックリンクを作成
    rm -f "$release_dir/.env"
    rm -rf "$release_dir/logs" "$release_dir/media"
    
    sudo -u www-data ln -sf "$SHARED_DIR/.env" "$release_dir/.env"
    sudo -u www-data ln -sf "$SHARED_DIR/logs" "$release_dir/logs"
    sudo -u www-data ln -sf "$SHARED_DIR/media" "$release_dir/media"
    
    # 現在のリンクを作成
    rm -rf "$CURRENT_LINK"
    ln -sf "$release_dir" "$CURRENT_LINK"
    
    # バージョン情報を記録
    echo "$initial_version" > "$BASE_DIR/current_version"
    
    log "✅ 既存アプリケーションを $initial_version として移行しました"
}

# 古いアプリケーションディレクトリの削除確認
cleanup_old_directory() {
    log "古いアプリケーションディレクトリのクリーンアップ..."
    
    if [ -d "$OLD_APP_DIR" ] && [ "$OLD_APP_DIR" != "$CURRENT_LINK" ]; then
        read -p "古いアプリケーションディレクトリ ($OLD_APP_DIR) を削除しますか? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$OLD_APP_DIR"
            log "✅ 古いアプリケーションディレクトリを削除しました"
        else
            log "古いアプリケーションディレクトリは保持されます"
        fi
    fi
}

# systemdサービスの更新
update_systemd_service() {
    log "systemdサービスを更新しています..."
    
    # 新しいパスでサービスファイルを更新
    if [ -f "/etc/systemd/system/diary-gunicorn.service" ]; then
        sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_LINK|g" /etc/systemd/system/diary-gunicorn.service
        sed -i "s|ExecStart=.*|ExecStart=$CURRENT_LINK/venv/bin/gunicorn --config $CURRENT_LINK/gunicorn.conf.py config.wsgi:application|g" /etc/systemd/system/diary-gunicorn.service
        
        systemctl daemon-reload
        log "✅ systemdサービスを更新しました"
    else
        log "⚠️  diary-gunicorn.service が見つかりません"
    fi
}

# Nginx設定の更新
update_nginx_config() {
    log "Nginx設定を更新しています..."
    
    if [ -f "/etc/nginx/sites-available/diary" ]; then
        # 新しいパスでNginx設定を更新
        sed -i "s|root .*;|root $CURRENT_LINK/static;|g" /etc/nginx/sites-available/diary
        sed -i "s|alias .*media;|alias $SHARED_DIR/media;|g" /etc/nginx/sites-available/diary
        
        nginx -t && systemctl reload nginx
        log "✅ Nginx設定を更新しました"
    else
        log "⚠️  Nginx設定ファイルが見つかりません"
    fi
}

# 動作確認
verify_setup() {
    log "セットアップの動作確認を行っています..."
    
    # サービスの再起動
    systemctl restart diary-gunicorn
    systemctl restart nginx
    
    # ヘルスチェック実行
    sleep 5
    if bash "$SCRIPTS_DIR/health-check.sh"; then
        log "✅ セットアップが正常に完了しました"
    else
        log "⚠️  ヘルスチェックで問題が検出されました"
    fi
}

# 使用方法の表示
show_usage_instructions() {
    log "=== セットアップ完了 ==="
    echo ""
    echo "新しいデプロイシステムが正常にセットアップされました。"
    echo ""
    echo "📁 ディレクトリ構造:"
    echo "  $RELEASES_DIR/     - リリース版の保存場所"
    echo "  $SHARED_DIR/       - 共有ファイル（.env, logs, media）"
    echo "  $SCRIPTS_DIR/      - デプロイスクリプト"
    echo "  $CURRENT_LINK      - 現在のアプリケーション（シンボリックリンク）"
    echo ""
    echo "🚀 使用方法:"
    echo "  デプロイ:     bash $SCRIPTS_DIR/deploy-with-rollback.sh deploy v1.0.0 https://github.com/user/repo.git"
    echo "  ロールバック: bash $SCRIPTS_DIR/deploy-with-rollback.sh rollback"
    echo "  リリース一覧: bash $SCRIPTS_DIR/deploy-with-rollback.sh list"
    echo "  ヘルスチェック: bash $SCRIPTS_DIR/health-check.sh"
    echo ""
    echo "🔧 GitHub Actionsの設定:"
    echo "  1. .github/workflows/deploy-improved.yml を使用してください"
    echo "  2. GitHub Secretsに以下を設定してください:"
    echo "     - EC2_HOST: サーバーのIPアドレス"
    echo "     - EC2_USERNAME: SSHユーザー名"
    echo "     - EC2_SSH_KEY: SSH秘密鍵"
    echo ""
    echo "📋 次のステップ:"
    echo "  1. $SHARED_DIR/.env ファイルの設定を確認してください"
    echo "  2. GitHub Actionsでデプロイをテストしてください"
    echo "  3. ロールバック機能をテストしてください"
}

# メイン処理
main() {
    log "=== ロールバック対応デプロイシステムのセットアップを開始します ==="
    
    check_permissions
    backup_existing_system
    setup_directory_structure
    migrate_env_file
    migrate_media_files
    migrate_log_files
    copy_scripts
    migrate_current_app
    update_systemd_service
    update_nginx_config
    verify_setup
    cleanup_old_directory
    show_usage_instructions
    
    log "✅ セットアップが完了しました"
}

# 使用方法表示
usage() {
    echo "ロールバック対応デプロイシステムのセットアップスクリプト"
    echo ""
    echo "使用方法:"
    echo "  sudo $0"
    echo ""
    echo "このスクリプトは既存のDjangoアプリケーションを"
    echo "ロールバック機能付きの新しいデプロイシステムに移行します。"
}

# 引数チェック
case "${1:-}" in
    --help|-h)
        usage
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "不明なオプション: $1"
        usage
        exit 1
        ;;
esac
