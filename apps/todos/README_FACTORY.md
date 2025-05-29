# Factory Boy を使った Todo Fixtures

このドキュメントでは、Factory Boyを使ってTodoアプリのテストデータを作成する方法について説明します。

## Factory Boyとは

Factory Boyは、Djangoのテストデータを簡単に作成するためのライブラリです。モデルのインスタンスを効率的に生成し、テストやデータベースの初期化に使用できます。

## 作成したFactory

### 1. TodoFactory (基本Factory)
```python
from apps.todos.factories import TodoFactory

# 単一のTodoを作成
todo = TodoFactory()

# 複数のTodoを作成
todos = TodoFactory.create_batch(5)

# カスタム属性を指定
todo = TodoFactory(title="カスタムタイトル", description="カスタム説明")

# DBに保存せずにインスタンスのみ作成
todo = TodoFactory.build()
```

### 2. CompletedTodoFactory (完了済みTodo)
```python
from apps.todos.factories import CompletedTodoFactory

# 完了済みのTodoを作成
completed_todo = CompletedTodoFactory()
print(completed_todo.completed_at)  # 完了日時が設定されている
```

### 3. IncompleteTodoFactory (未完了Todo)
```python
from apps.todos.factories import IncompleteTodoFactory

# 未完了のTodoを作成
incomplete_todo = IncompleteTodoFactory()
print(incomplete_todo.completed_at)  # None
```

### 4. TodoWithoutDescriptionFactory (説明なしTodo)
```python
from apps.todos.factories import TodoWithoutDescriptionFactory

# 説明なしのTodoを作成
todo = TodoWithoutDescriptionFactory()
print(todo.description)  # None
```

### 5. TodoWithShortDescriptionFactory (短い説明のTodo)
```python
from apps.todos.factories import TodoWithShortDescriptionFactory

# 短い説明のTodoを作成
todo = TodoWithShortDescriptionFactory()
print(len(todo.description))  # 短い説明文
```

## テストでの使用例

```python
from django.test import TestCase
from apps.todos.factories import TodoFactory, CompletedTodoFactory

class TodoViewTest(TestCase):
    def setUp(self):
        # テスト用のTodoデータを作成
        self.todos = TodoFactory.create_batch(3)
        self.completed_todo = CompletedTodoFactory()
    
    def test_todo_list_view(self):
        # テストコード
        pass
```

## 管理コマンドでの使用

サンプルデータを作成するための管理コマンドも用意されています：

```bash
# 10件のサンプルTodoを作成
python manage.py create_sample_todos

# 20件のサンプルTodoを作成
python manage.py create_sample_todos --count 20

# 既存データを削除してから作成
python manage.py create_sample_todos --clear
```

## Factory Boyの主要機能

### 1. Faker統合
```python
title = factory.Faker('sentence', nb_words=4, locale='ja_JP')
description = factory.Faker('text', max_nb_chars=200, locale='ja_JP')
```

### 2. LazyAttribute
```python
updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
```

### 3. Sequence
```python
title = factory.Sequence(lambda n: f"Todo {n}")
```

### 4. SubFactory（関連モデル用）
```python
# 例：将来的にUserモデルが追加された場合
author = factory.SubFactory(UserFactory)
```

## テスト実行

作成したテストを実行するには：

```bash
# 全てのテストを実行
poetry run python manage.py test apps.todos

# 特定のテストクラスのみ実行
poetry run python manage.py test apps.todos.tests.TodoModelTest

# テストデータベースを保持して高速実行（推奨）
poetry run python manage.py test apps.todos --keepdb --verbosity=2

# pytestを使用する場合（設定でreuse-dbが有効）
poetry run pytest apps/todos/tests.py -v
```

### テスト実行の最適化

- `--keepdb`オプション: テストデータベースを保持し、次回実行時に再利用
- `--verbosity=2`オプション: 詳細な実行結果を表示
- pytestの場合: pyproject.tomlで`--reuse-db`が設定済み
```

## 注意事項

1. **日本語ロケール**: Fakerで日本語データを生成するため、`locale='ja_JP'`を指定しています
2. **タイムゾーン**: `timezone.get_current_timezone()`を使用してタイムゾーンを適切に設定
3. **データベース**: テスト実行時は自動的にテスト用データベースが使用されます
4. **パフォーマンス**: 大量のデータを作成する場合は`create_batch()`を使用してください

## 拡張例

将来的にUserモデルやCategoryモデルが追加された場合の拡張例：

```python
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')

class TodoWithUserFactory(TodoFactory):
    author = factory.SubFactory(UserFactory)
```

このように、Factory Boyを使用することで、テストデータの作成が簡単かつ一貫性を保って行えます。
