#!/bin/bash

# ロールバック機能付きデプロイスクリプト
# 使用方法:
#   deploy-with-rollback.sh deploy <version> <repo_url>
#   deploy-with-rollback.sh rollback [version]
#   deploy-with-rollback.sh list

set -e

# 設定
APP_NAME="diary"
BASE_DIR="/var/www"
RELEASES_DIR="$BASE_DIR/releases"
CURRENT_LINK="$BASE_DIR/$APP_NAME"
SHARED_DIR="$BASE_DIR/shared"
DEPLOY_LOG="$BASE_DIR/deploy.log"
MAX_RELEASES=5  # 保持する最大リリース数

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DEPLOY_LOG"
}

# エラーハンドリング
error_exit() {
    log "ERROR: $1"
    exit 1
}

# ディレクトリ初期化
init_directories() {
    log "ディレクトリを初期化しています..."
    
    # 必要なディレクトリを作成
    sudo mkdir -p "$RELEASES_DIR" "$SHARED_DIR"
    sudo chown -R www-data:www-data "$BASE_DIR"
    
    # 共有ディレクトリの初期化
    sudo -u www-data mkdir -p "$SHARED_DIR/logs"
    sudo -u www-data mkdir -p "$SHARED_DIR/media"
    sudo -u www-data mkdir -p "$SHARED_DIR/static"
    
    # .envファイルが存在しない場合は作成
    if [ ! -f "$SHARED_DIR/.env" ]; then
        log ".envファイルのテンプレートを作成しています..."
        sudo -u www-data cat > "$SHARED_DIR/.env" << 'EOF'
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
        log "⚠️  $SHARED_DIR/.env ファイルを編集して正しい値を設定してください"
    fi
}

# デプロイ関数
deploy() {
    local version="$1"
    local repo_url="$2"
    
    if [ -z "$version" ] || [ -z "$repo_url" ]; then
        error_exit "バージョンとリポジトリURLが必要です"
    fi
    
    log "=== デプロイを開始します (バージョン: $version) ==="
    
    # ディレクトリ初期化
    init_directories
    
    # リリースディレクトリ作成
    local release_dir="$RELEASES_DIR/$version"
    
    if [ -d "$release_dir" ]; then
        log "バージョン $version は既に存在します。スキップします。"
        switch_version "$version"
        return 0
    fi
    
    log "リリースディレクトリを作成: $release_dir"
    sudo -u www-data mkdir -p "$release_dir"
    
    # コードのクローン
    log "コードをクローンしています..."
    if [[ "$version" == main-* ]]; then
        # mainブランチの場合
        sudo -u www-data git clone "$repo_url" "$release_dir"
        cd "$release_dir"
        sudo -u www-data git checkout main
    else
        # タグの場合
        sudo -u www-data git clone --branch "$version" --depth 1 "$repo_url" "$release_dir"
    fi
    
    cd "$release_dir"
    
    # 共有ファイルのシンボリックリンク作成
    log "共有ファイルのシンボリックリンクを作成しています..."
    sudo -u www-data ln -sf "$SHARED_DIR/.env" "$release_dir/.env"
    sudo -u www-data ln -sf "$SHARED_DIR/logs" "$release_dir/logs"
    sudo -u www-data ln -sf "$SHARED_DIR/media" "$release_dir/media"
    
    # 仮想環境の作成
    log "仮想環境を作成しています..."
    sudo -u www-data python3 -m venv venv
    
    # 依存関係のインストール
    log "依存関係をインストールしています..."
    sudo -u www-data venv/bin/pip install --upgrade pip
    sudo -u www-data venv/bin/pip install poetry
    sudo -u www-data venv/bin/poetry install --only=main
    
    # データベースマイグレーション
    log "データベースマイグレーションを実行しています..."
    sudo -u www-data venv/bin/python manage.py migrate
    
    # 静的ファイルの収集
    log "静的ファイルを収集しています..."
    sudo -u www-data venv/bin/python manage.py collectstatic --noinput
    
    # バージョンを切り替え
    switch_version "$version"
    
    # 古いリリースを削除
    cleanup_old_releases
    
    log "✅ デプロイが完了しました (バージョン: $version)"
}

# バージョン切り替え関数
switch_version() {
    local version="$1"
    local release_dir="$RELEASES_DIR/$version"
    
    if [ ! -d "$release_dir" ]; then
        error_exit "バージョン $version が見つかりません"
    fi
    
    log "バージョンを切り替えています: $version"
    
    # 現在のバージョンを記録
    if [ -L "$CURRENT_LINK" ]; then
        local current_version=$(basename $(readlink "$CURRENT_LINK"))
        echo "$current_version" > "$BASE_DIR/previous_version"
    fi
    
    # シンボリックリンクを更新
    sudo rm -f "$CURRENT_LINK"
    sudo ln -sf "$release_dir" "$CURRENT_LINK"
    
    # 現在のバージョンを記録
    echo "$version" > "$BASE_DIR/current_version"
    
    # サービスを再起動
    log "サービスを再起動しています..."
    sudo systemctl restart diary-gunicorn
    sudo systemctl restart nginx
    
    log "✅ バージョン $version に切り替えました"
}

# ロールバック関数
rollback() {
    local target_version="$1"
    
    if [ -z "$target_version" ]; then
        # 前のバージョンにロールバック
        if [ -f "$BASE_DIR/previous_version" ]; then
            target_version=$(cat "$BASE_DIR/previous_version")
        else
            error_exit "前のバージョンが見つかりません"
        fi
    fi
    
    log "=== ロールバックを開始します (バージョン: $target_version) ==="
    
    switch_version "$target_version"
    
    log "✅ ロールバックが完了しました (バージョン: $target_version)"
}

# 古いリリースのクリーンアップ
cleanup_old_releases() {
    log "古いリリースをクリーンアップしています..."
    
    cd "$RELEASES_DIR"
    local releases=($(ls -1t))
    local count=${#releases[@]}
    
    if [ $count -gt $MAX_RELEASES ]; then
        local to_remove=$((count - MAX_RELEASES))
        for ((i=MAX_RELEASES; i<count; i++)); do
            local release="${releases[$i]}"
            log "古いリリースを削除: $release"
            sudo rm -rf "$RELEASES_DIR/$release"
        done
    fi
}

# リリース一覧表示
list_releases() {
    log "=== デプロイ済みリリース一覧 ==="
    
    if [ ! -d "$RELEASES_DIR" ]; then
        log "リリースディレクトリが存在しません"
        return 1
    fi
    
    cd "$RELEASES_DIR"
    local releases=($(ls -1t))
    
    if [ ${#releases[@]} -eq 0 ]; then
        log "デプロイ済みリリースがありません"
        return 1
    fi
    
    local current_version=""
    if [ -f "$BASE_DIR/current_version" ]; then
        current_version=$(cat "$BASE_DIR/current_version")
    fi
    
    for release in "${releases[@]}"; do
        if [ "$release" = "$current_version" ]; then
            log "  $release (現在)"
        else
            log "  $release"
        fi
    done
}

# 使用方法表示
usage() {
    echo "使用方法:"
    echo "  $0 deploy <version> <repo_url>  - 指定されたバージョンをデプロイ"
    echo "  $0 rollback [version]           - 前のバージョンまたは指定されたバージョンにロールバック"
    echo "  $0 list                         - デプロイ済みリリース一覧を表示"
    echo ""
    echo "例:"
    echo "  $0 deploy v1.0.0 https://github.com/user/repo.git"
    echo "  $0 rollback"
    echo "  $0 rollback v1.0.0"
    echo "  $0 list"
}

# メイン処理
case "${1:-}" in
    deploy)
        deploy "$2" "$3"
        ;;
    rollback)
        rollback "$2"
        ;;
    list)
        list_releases
        ;;
    *)
        usage
        exit 1
        ;;
esac
