# DjangoでのE2Eテスト実装ガイド（Playwright版）

このプロジェクトでは、TodoアプリケーションのE2E（End-to-End）テストをPlaywrightを使用して実装しています。

## 概要

E2Eテストは、実際のブラウザを使用してアプリケーション全体の動作をテストする手法です。ユーザーの操作をシミュレートし、アプリケーションが期待通りに動作することを確認します。

## なぜPlaywrightを選んだか

- **高速**: Seleniumより高速な実行
- **モダンAPI**: 非同期処理とモダンなAPI
- **簡単セットアップ**: ブラウザの自動インストール
- **パフォーマンステスト**: ページロード時間の測定機能
- **安定性**: 最新のWeb技術に対応

## 実装されているテスト

### Playwrightベースのテスト (`apps/todos/test_e2e_playwright.py`)

- **test_todo_crud_flow_playwright**: Todo CRUD操作の一連の流れをテスト
- **test_todo_validation_errors_playwright**: バリデーションエラーのテスト
- **test_todo_performance_playwright**: パフォーマンステスト

## セットアップ

### 1. 依存関係のインストール

```bash
# 依存関係をインストール
poetry install

# 依存関係をチェック
python run_e2e_tests.py --check-deps
```

### 2. Playwrightブラウザのインストール

```bash
# Playwrightブラウザをインストール
python run_e2e_tests.py --install-browsers
```

## テストの実行

### 基本的な実行方法

```bash
# E2Eテストを実行
python run_e2e_tests.py
```

### Djangoのテストコマンドを直接使用

```bash
# Playwrightテストを実行
python manage.py test apps.todos.test_e2e_playwright --settings=config.test_settings
```

## ファイル構成

```
├── apps/todos/
│   └── test_e2e_playwright.py    # PlaywrightベースのE2Eテスト
├── config/
│   └── test_settings.py          # E2Eテスト用の設定ファイル
├── run_e2e_tests.py              # E2Eテスト実行スクリプト
└── E2E_TESTING_README.md         # このファイル
```

## テスト設定

### E2Eテスト用設定 (`config/test_settings.py`)

- SQLiteインメモリデータベースを使用
- デバッグツールバーを無効化
- 高速なパスワードハッシュ化
- テスト用ログ設定

## テストケースの詳細

### CRUD操作テスト

1. ユーザーログイン
2. Todo一覧ページの表示確認
3. Todo作成
4. Todo詳細表示
5. Todo編集
6. Todo削除

### バリデーションテスト

1. 空のフォーム送信
2. タイトルの文字数制限
3. 説明の文字数制限

### パフォーマンステスト

1. ページロード時間の測定
2. Todo作成時間の測定
3. 複数データでの一覧表示性能

## Playwrightの特徴

### 高速実行
- 並列実行サポート
- 効率的なブラウザ制御
- 最適化されたAPI

### モダンAPI
- 非同期処理（async/await）
- 直感的なセレクタ
- 豊富な待機オプション

### 自動化機能
- ブラウザの自動インストール
- スクリーンショット自動撮影
- ネットワーク監視

## トラブルシューティング

### よくある問題

1. **Playwrightブラウザが見つからない**
   ```bash
   python run_e2e_tests.py --install-browsers
   ```

2. **テストが失敗する**
   - ログを確認してエラーの詳細を把握
   - ヘッドレスモードを無効化してデバッグ
   - テスト環境の設定を確認

### デバッグ方法

1. **ヘッドレスモードを無効化**
   ```python
   # test_e2e_playwright.pyで
   self.browser = await self.playwright.chromium.launch(headless=False)
   ```

2. **詳細ログの有効化**
   ```bash
   python manage.py test apps.todos.test_e2e_playwright --settings=config.test_settings --verbosity=3
   ```

3. **スクリーンショット撮影**
   ```python
   await self.page.screenshot(path='debug.png')
   ```

## ベストプラクティス

### 1. テストの独立性

- 各テストは独立して実行可能
- テスト間でデータを共有しない
- setUp/tearDownで適切にクリーンアップ

### 2. 待機戦略

- `wait_for_selector`を使用して要素の存在を確認
- `wait_for_load_state`でページロード完了を待機
- タイムアウト値を適切に設定

### 3. セレクタの選択

- `input[name="title"]`のような属性セレクタを使用
- `text=新規作成`のようなテキストセレクタを活用
- IDやクラス名を適切に使用

### 4. 非同期処理

- すべてのPlaywright操作に`await`を使用
- 非同期コンテキストマネージャーを適切に使用
- エラーハンドリングを忘れずに実装

## CI/CD統合

### GitHub Actions例

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    
    - name: Install Playwright browsers
      run: |
        poetry run python run_e2e_tests.py --install-browsers
    
    - name: Run E2E tests
      run: |
        poetry run python run_e2e_tests.py
```

## パフォーマンス最適化

### テスト実行の高速化

1. **並列実行**
   ```bash
   python manage.py test apps.todos.test_e2e_playwright --parallel
   ```

2. **ブラウザの再利用**
   - クラスレベルでブラウザインスタンスを共有
   - ページのみを新規作成

3. **不要な要素の無効化**
   - 画像の読み込み無効化
   - CSSの読み込み無効化（必要に応じて）

## まとめ

PlaywrightによるE2Eテスト実装により、TodoアプリケーションのUIとユーザーフローが正常に動作することを効率的に検証できます。

Playwrightの高速性とモダンなAPIにより、開発サイクルに組み込みやすいテストスイートを構築できます。定期的にE2Eテストを実行し、アプリケーションの品質を維持しましょう。
