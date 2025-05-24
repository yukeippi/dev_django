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

このプロジェクトはPoetryを使用して依存関係を管理しています。以下のコマンドを実行して、Django の開発サーバーを起動できます：

```bash
# 依存関係のインストール（初回のみ）
poetry install

# 開発サーバーの起動
poetry run python manage.py runserver 0.0.0.0:8000
```

または、Poetry の仮想環境をアクティベートしてからコマンドを実行することもできます：

```bash
# 仮想環境のアクティベート
poetry shell

# 開発サーバーの起動
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
# Poetry環境内でアプリケーションを作成
poetry run python manage.py startapp <アプリケーション名>

# または、仮想環境をアクティベートしてから実行
poetry shell
python manage.py startapp <アプリケーション名>
```

作成したアプリケーションを使用するには、`config/settings.py` の `INSTALLED_APPS` リストに追加します。

### その他のDjangoコマンド

すべてのDjangoコマンドは `poetry run` を前に付けて実行するか、`poetry shell` で仮想環境をアクティベートしてから実行してください：

```bash
# マイグレーションの作成
poetry run python manage.py makemigrations

# マイグレーションの実行
poetry run python manage.py migrate

# スーパーユーザーの作成
poetry run python manage.py createsuperuser

# 静的ファイルの収集
poetry run python manage.py collectstatic
```

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

## CI/CD（GitHub Actions）

このプロジェクトでは、GitHub Actionsを使用した自動テスト・デプロイシステムを構築しています。

### ワークフローの動作

#### トリガー条件
1. **developブランチへのpush**: コードがdevelopブランチにマージされた時
2. **タグpush**: `v*`形式のタグ（例：v1.0.0）がpushされた時
3. **プルリクエスト**: developブランチに対するPR作成・更新時
4. **手動実行**: GitHub ActionsのUIから手動でワークフローを実行

#### ジョブ構成

**1. testジョブ**
- **実行条件**: 全てのトリガーで実行
- **環境**: Ubuntu最新版 + PostgreSQL 15
- **処理内容**:
  - Python 3.11のセットアップ
  - Poetryのインストール
  - 依存関係のキャッシュ利用・インストール
  - Djangoテストの実行

**2. deployジョブ**
- **実行条件**: 
  - developブランチへのpush
  - タグpush
  - 手動実行（deployアクション選択時）
- **前提条件**: testジョブの成功
- **処理内容**:
  - バージョン決定（develop-YYYYMMDD-HHMMSS形式またはタグ名）
  - EC2サーバーでデプロイスクリプト実行
  - ヘルスチェック実行
  - 失敗時の自動ロールバック

**3. rollbackジョブ**
- **実行条件**: 手動実行でrollbackアクション選択時
- **処理内容**:
  - 指定バージョンまたは前バージョンへのロールバック
  - ロールバック後のヘルスチェック

#### 手動実行オプション
- **deploy**: 通常のデプロイ実行
- **rollback**: ロールバック実行
- **version**: デプロイ・ロールバック対象バージョンの指定（オプション）

#### 特徴
- **自動テスト**: デプロイ前に必ずテストが実行される
- **ロールバック機能**: デプロイ失敗時の自動復旧とマニュアル復旧
- **ヘルスチェック**: デプロイ後の動作確認
- **バージョン管理**: デプロイごとのバージョン追跡
- **柔軟な実行**: 自動・手動両方の実行方式をサポート

### デプロイ環境の設定

GitHub Actionsでデプロイを実行するには、以下のシークレットを設定する必要があります：

- `EC2_HOST`: デプロイ先EC2インスタンスのホスト名またはIPアドレス
- `EC2_USERNAME`: EC2インスタンスのユーザー名
- `EC2_SSH_KEY`: EC2インスタンスへのSSH接続用の秘密鍵

## カスタマイズ

- `.devcontainer/devcontainer.json`: VS Code の設定や拡張機能を変更できます
- `.devcontainer/docker-compose.yml`: Docker サービスの設定を変更できます
- `.devcontainer/Dockerfile`: Python 環境のカスタマイズができます
- `pyproject.toml`: Poetry を使用した Python パッケージの依存関係を管理できます
- `.github/workflows/deploy.yml`: CI/CDパイプラインの設定を変更できます
