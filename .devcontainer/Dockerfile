FROM python:3.11

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリの設定
WORKDIR /workspace

# 必要なパッケージのインストール（Playwright依存関係を含む）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    gettext \
    git \
    vim \
    curl \
    wget \
    htop \
    net-tools \
    zsh \
    unzip \
    # Playwright用の依存関係
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libcups2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI (gh)のインストール
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python パッケージのインストール
RUN pip install --upgrade pip \
    && pip install black pylint isort

# 非root ユーザーの作成
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# デフォルトのシェルを bash に設定
ENV SHELL /bin/bash

# ポート 8000 を公開
EXPOSE 8000

# ユーザーを vscode に切り替え
USER $USERNAME
