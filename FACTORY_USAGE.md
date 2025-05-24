# Factory Bot for Python/Django - 使用方法

このプロジェクトでは、RailsのFactory Botに相当する**factory_boy**ライブラリを使用しています。

## インストール済みライブラリ

- `factory-boy`: テストデータ生成用のファクトリライブラリ
- `faker`: ダミーデータ生成ライブラリ（日本語対応）

## ファクトリの場所

- `diary/factories.py`: 各モデル用のファクトリ定義
- `diary/test_factories.py`: ファクトリの使用例とテスト

## 基本的な使用方法

### 1. 単一オブジェクトの作成

```python
from diary.factories import UserFactory, DiaryEntryFactory, DiaryCommentFactory

# ユーザーを作成（DBに保存される）
user = UserFactory()

# 日記エントリを作成
entry = DiaryEntryFactory()

# コメントを作成
comment = DiaryCommentFactory()
```

### 2. カスタム属性での作成

```python
# 特定の属性を指定して作成
user = UserFactory(username='test_user')
entry = DiaryEntryFactory(
    title='テストタイトル',
    content='これはテスト用のコンテンツです。最低10文字以上必要です。',
    author=user
)
```

### 3. 関連オブジェクトの作成

```python
# 特定の日記に複数のコメントを作成
entry = DiaryEntryFactory()
comments = DiaryCommentFactory.create_batch(3, diary=entry)

# 特定のユーザーが作成した複数の日記
user = UserFactory()
entries = DiaryEntryFactory.create_batch(5, author=user)
```

### 4. 保存せずにオブジェクトを作成

```python
# メモリ上にのみ作成（DBに保存しない）
entry = DiaryEntryFactory.build()
print(entry.pk)  # None

# 後で手動保存
entry.save()
print(entry.pk)  # 1
```

### 5. バッチ作成

```python
# 複数のオブジェクトを一度に作成
entries = DiaryEntryFactory.create_batch(10)
users = UserFactory.create_batch(5)
```

## テストでの使用例

```python
import pytest
from diary.factories import DiaryEntryFactory, UserFactory

@pytest.mark.django_db
def test_diary_entry_creation():
    """日記エントリ作成のテスト"""
    entry = DiaryEntryFactory()
    assert entry.title
    assert len(entry.content) >= 10
    assert entry.author

@pytest.mark.django_db
def test_user_with_multiple_entries():
    """ユーザーが複数の日記を持つテスト"""
    user = UserFactory()
    entries = DiaryEntryFactory.create_batch(3, author=user)
    
    assert user.diaryentry_set.count() == 3
```

## 他のファクトリライブラリとの比較

### factory_boy vs model_bakery

| 特徴 | factory_boy | model_bakery |
|------|-------------|--------------|
| 人気度 | ★★★★★ | ★★★☆☆ |
| Django特化 | ☆☆☆☆☆ | ★★★★★ |
| 設定の柔軟性 | ★★★★★ | ★★★☆☆ |
| 学習コスト | 中 | 低 |

### model_bakeryの使用例（参考）

```python
# model_bakeryを使用する場合
from model_bakery import baker

# 簡単な作成
entry = baker.make('diary.DiaryEntry')

# 関連オブジェクト付きで作成
entry = baker.make('diary.DiaryEntry', author__username='test_user')

# 複数作成
entries = baker.make('diary.DiaryEntry', _quantity=5)
```

## 推奨事項

1. **factory_boy**を使用することを推奨（より柔軟で機能豊富）
2. テストファイルでは`@pytest.mark.django_db`デコレータを忘れずに
3. 日本語のダミーデータが必要な場合は`Faker('ja_JP')`を使用
4. 複雑な関連性がある場合は`SubFactory`を活用
5. パフォーマンステストでは`build()`を使用してDB保存を避ける

## 実行方法

```bash
# ファクトリのテストを実行
poetry run pytest diary/test_factories.py -v

# 全テストを実行
poetry run pytest -v
