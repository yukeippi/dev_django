# Python 3.11のスリムイメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Poetryをインストール
RUN pip install poetry

# Poetryの設定（仮想環境を作成しない）
ENV POETRY_VENV_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# 依存関係ファイルをコピー
COPY pyproject.toml poetry.lock ./

# 依存関係をインストール（開発依存関係は除外）
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# アプリケーションコードをコピー
COPY . .

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput

# 非rootユーザーを作成
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# ポート8000を公開
EXPOSE 8000

# Gunicornでアプリケーションを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
