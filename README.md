# Django PostgreSQL 開発環境

このリポジトリは、Django と PostgreSQL を使用した Web アプリケーション開発のための devcontainer 環境です。VS Code の Remote - Containers 拡張機能を使用して、簡単に開発環境を構築できます。

## 前提条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Remote - Containers 拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## 使い方

### 環境のセットアップ

1. このリポジトリをクローンします：
   ```bash
   git clone <リポジトリの URL>
   cd <リポジトリ名>
   ```

2. VS Code でフォルダを開きます：
   ```bash
   code .
   ```

3. VS Code の左下にある「><」アイコンをクリックし、「Reopen in Container」を選択します。
   - 初回起動時は、Docker イメージのビルドに数分かかることがあります。

4. コンテナ内で Django プロジェクトが起動します。

### 開発の開始

コンテナ内で以下のコマンドを実行して、Django の開発サーバーを起動できます：

```bash
python manage.py runserver 0.0.0.0:8000
```

ブラウザで http://localhost:8000 にアクセスして、Django アプリケーションを確認できます。

### データベース接続情報

PostgreSQL データベースには以下の情報で接続できます：

- ホスト: `db`
- ポート: `5432`
- データベース名: `postgres`
- ユーザー名: `postgres`
- パスワード: `postgres`

### 新しいアプリケーションの作成

新しい Django アプリケーションを作成するには、以下のコマンドを実行します：

```bash
python manage.py startapp <アプリケーション名>
```

作成したアプリケーションを使用するには、`config/settings.py` の `INSTALLED_APPS` リストに追加します。

## 環境の構成

### ディレクトリ構造

- `.devcontainer/`: VS Code devcontainer の設定ファイル
- `config/`: Django プロジェクトの設定ファイル
- `apps/`: Django アプリケーションを格納するディレクトリ
- `static/`: 静的ファイル用のディレクトリ
- `templates/`: テンプレートファイル用のディレクトリ

### 主な機能

- Django 4.2.x
- PostgreSQL 14
- Python 3.11
- VS Code の拡張機能（Python、Django、Docker など）
- デバッグツール（Django Debug Toolbar）
- コード品質ツール（Black、Pylint、isort）

## カスタマイズ

- `.devcontainer/devcontainer.json`: VS Code の設定や拡張機能を変更できます
- `.devcontainer/docker-compose.yml`: Docker サービスの設定を変更できます
- `.devcontainer/Dockerfile`: Python 環境のカスタマイズができます
- `requirements.txt`: Python パッケージの依存関係を管理できます
