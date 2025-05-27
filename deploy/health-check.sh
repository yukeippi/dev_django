#!/bin/bash

# ヘルスチェックスクリプト
# アプリケーションの健全性を確認します

set -e

# 設定
APP_NAME="diary"
BASE_DIR="/var/www"
CURRENT_LINK="$BASE_DIR/$APP_NAME"
HEALTH_CHECK_URL="http://localhost:8000/health/"
BACKUP_HEALTH_CHECK_URL="http://localhost/"
MAX_RETRIES=5
RETRY_INTERVAL=10
TIMEOUT=30

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] HEALTH_CHECK: $1"
}

# エラーハンドリング
error_exit() {
    log "ERROR: $1"
    exit 1
}

# サービス状態チェック
check_services() {
    log "サービス状態をチェックしています..."
    
    # Gunicornサービスの状態確認
    if ! systemctl is-active --quiet diary-gunicorn; then
        error_exit "diary-gunicornサービスが停止しています"
    fi
    log "✅ diary-gunicornサービスは正常に動作しています"
    
    # Nginxサービスの状態確認
    if ! systemctl is-active --quiet nginx; then
        error_exit "nginxサービスが停止しています"
    fi
    log "✅ nginxサービスは正常に動作しています"
}

# プロセス確認
check_processes() {
    log "プロセスをチェックしています..."
    
    # Gunicornプロセスの確認
    if ! pgrep -f "gunicorn.*diary" > /dev/null; then
        error_exit "Gunicornプロセスが見つかりません"
    fi
    log "✅ Gunicornプロセスが動作しています"
    
    # Nginxプロセスの確認
    if ! pgrep nginx > /dev/null; then
        error_exit "Nginxプロセスが見つかりません"
    fi
    log "✅ Nginxプロセスが動作しています"
}

# ポート確認
check_ports() {
    log "ポートをチェックしています..."
    
    # Gunicornポート（8000）の確認
    if ! netstat -tuln | grep -q ":8000 "; then
        error_exit "ポート8000でリッスンしているプロセスが見つかりません"
    fi
    log "✅ ポート8000でリッスンしています"
    
    # Nginxポート（80）の確認
    if ! netstat -tuln | grep -q ":80 "; then
        error_exit "ポート80でリッスンしているプロセスが見つかりません"
    fi
    log "✅ ポート80でリッスンしています"
}

# HTTPレスポンス確認
check_http_response() {
    local url="$1"
    local expected_status="$2"
    local retry_count=0
    
    log "HTTPレスポンスをチェックしています: $url"
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$url" || echo "000")
        
        if [ "$status_code" = "$expected_status" ]; then
            log "✅ HTTPレスポンス正常: $status_code"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log "⚠️  HTTPレスポンス異常: $status_code (試行 $retry_count/$MAX_RETRIES)"
        
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log "   $RETRY_INTERVAL秒後に再試行します..."
            sleep $RETRY_INTERVAL
        fi
    done
    
    error_exit "HTTPレスポンスチェックに失敗しました: $url (最終ステータス: $status_code)"
}

# データベース接続確認
check_database() {
    log "データベース接続をチェックしています..."
    
    if [ ! -L "$CURRENT_LINK" ]; then
        error_exit "現在のアプリケーションリンクが見つかりません"
    fi
    
    cd "$CURRENT_LINK"
    
    # Django管理コマンドでデータベース接続を確認
    if ! sudo -u www-data venv/bin/python manage.py check --database default > /dev/null 2>&1; then
        error_exit "データベース接続に失敗しました"
    fi
    
    log "✅ データベース接続は正常です"
}

# ディスク容量確認
check_disk_space() {
    log "ディスク容量をチェックしています..."
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local threshold=90
    
    if [ "$usage" -gt "$threshold" ]; then
        log "⚠️  ディスク使用量が高いです: ${usage}%"
        # 警告のみで、エラーにはしない
    else
        log "✅ ディスク使用量は正常です: ${usage}%"
    fi
}

# メモリ使用量確認
check_memory() {
    log "メモリ使用量をチェックしています..."
    
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    local threshold=90
    
    if [ "$usage" -gt "$threshold" ]; then
        log "⚠️  メモリ使用量が高いです: ${usage}%"
        # 警告のみで、エラーにはしない
    else
        log "✅ メモリ使用量は正常です: ${usage}%"
    fi
}

# ログファイル確認
check_logs() {
    log "ログファイルをチェックしています..."
    
    # Gunicornのエラーログを確認
    local error_count=$(journalctl -u diary-gunicorn --since "5 minutes ago" --no-pager | grep -i error | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        log "⚠️  過去5分間にGunicornエラーが ${error_count} 件発生しています"
        # 最新のエラーを表示
        journalctl -u diary-gunicorn --since "5 minutes ago" --no-pager | grep -i error | tail -3
    else
        log "✅ Gunicornエラーログは正常です"
    fi
    
    # Nginxのエラーログを確認
    if [ -f "/var/log/nginx/error.log" ]; then
        local nginx_errors=$(tail -100 /var/log/nginx/error.log | grep "$(date '+%Y/%m/%d %H:')" | wc -l)
        if [ "$nginx_errors" -gt 0 ]; then
            log "⚠️  過去1時間にNginxエラーが ${nginx_errors} 件発生しています"
        else
            log "✅ Nginxエラーログは正常です"
        fi
    fi
}

# 総合ヘルスチェック
main() {
    log "=== ヘルスチェックを開始します ==="
    
    # 基本的なサービス確認
    check_services
    check_processes
    check_ports
    
    # アプリケーション確認
    check_database
    
    # HTTPレスポンス確認
    # まずヘルスチェックエンドポイントを試行
    if curl -s --connect-timeout 5 "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
        check_http_response "$HEALTH_CHECK_URL" "200"
    else
        # ヘルスチェックエンドポイントが無い場合はトップページを確認
        log "ヘルスチェックエンドポイントが見つかりません。トップページを確認します。"
        check_http_response "$BACKUP_HEALTH_CHECK_URL" "200"
    fi
    
    # システムリソース確認
    check_disk_space
    check_memory
    
    # ログ確認
    check_logs
    
    log "✅ すべてのヘルスチェックが完了しました"
    
    # 現在のバージョン情報を表示
    if [ -f "$BASE_DIR/current_version" ]; then
        local current_version=$(cat "$BASE_DIR/current_version")
        log "現在のバージョン: $current_version"
    fi
    
    return 0
}

# 使用方法表示
usage() {
    echo "使用方法:"
    echo "  $0                    - 総合ヘルスチェックを実行"
    echo "  $0 --services         - サービス状態のみチェック"
    echo "  $0 --http             - HTTPレスポンスのみチェック"
    echo "  $0 --database         - データベース接続のみチェック"
    echo "  $0 --resources        - システムリソースのみチェック"
}

# メイン処理
case "${1:-}" in
    --services)
        check_services
        check_processes
        check_ports
        ;;
    --http)
        if curl -s --connect-timeout 5 "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            check_http_response "$HEALTH_CHECK_URL" "200"
        else
            check_http_response "$BACKUP_HEALTH_CHECK_URL" "200"
        fi
        ;;
    --database)
        check_database
        ;;
    --resources)
        check_disk_space
        check_memory
        ;;
    --help)
        usage
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
