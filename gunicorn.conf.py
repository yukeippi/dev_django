"""
Gunicorn設定ファイル
"""

import multiprocessing

# サーバーソケット
bind = "127.0.0.1:8000"
backlog = 2048

# ワーカープロセス
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 再起動設定
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# ログ設定
accesslog = "/var/log/diary/gunicorn_access.log"
errorlog = "/var/log/diary/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# プロセス名
proc_name = "diary_gunicorn"

# ユーザー・グループ（必要に応じて設定）
# user = "www-data"
# group = "www-data"

# セキュリティ
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
