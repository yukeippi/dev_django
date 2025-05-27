import pytest
from django.utils import timezone

from apps.todos.models import Todo
from apps.todos.factories import (
    TodoFactory,
    CompletedTodoFactory,
    IncompleteTodoFactory,
    TodoWithoutDescriptionFactory
)


@pytest.fixture
def todo():
    """テスト用のTodoデータを準備するfixture"""
    return TodoFactory(
        title='テストTodo',
        description='これはテスト用のTodoです。'
    )


@pytest.mark.django_db
def test_create_todo(todo):
    """Todoの作成テスト"""
    assert todo.title == 'テストTodo'
    assert todo.description == 'これはテスト用のTodoです。'
    assert todo.created_at is not None
    assert todo.updated_at is not None
    assert todo.completed_at is None


@pytest.mark.django_db
def test_todo_str_method(todo):
    """__str__メソッドのテスト"""
    assert str(todo) == 'テストTodo'


@pytest.mark.django_db
def test_todo_ordering(todo):
    """Todoの並び順のテスト（Factory Boyを使用）"""
    todos = Todo.objects.all()
    assert todos[0] == todo  # 作成したTodoが最初に来るはず
    
    # Factory Boyを使ってさらに2つのTodoを作成
    todo2 = TodoFactory(title='テストTodo2')
    todo3 = TodoFactory(title='テストTodo3')
    
    todos = Todo.objects.all()
    assert todos[0] == todo3
    assert todos[1] == todo2
    assert todos[2] == todo


@pytest.mark.django_db
def test_completed_todo_behavior():
    """完了済みTodoの動作テスト"""
    completed_todo = CompletedTodoFactory()
    
    assert completed_todo.completed_at is not None
    assert isinstance(completed_todo.completed_at, timezone.datetime)


@pytest.mark.django_db
def test_incomplete_todo_behavior():
    """未完了Todoの動作テスト"""
    incomplete_todo = IncompleteTodoFactory()
    
    assert incomplete_todo.completed_at is None


@pytest.mark.django_db
def test_todo_without_description():
    """説明なしTodoの動作テスト"""
    todo_without_desc = TodoWithoutDescriptionFactory()
    
    assert todo_without_desc.description is None
    assert todo_without_desc.title is not None


@pytest.mark.django_db
def test_bulk_todo_creation():
    """複数のTodoを一括作成するテスト"""
    # 既存のTodoをクリア
    Todo.objects.all().delete()
    
    # Factory Boyを使って複数のTodoを作成
    todos = TodoFactory.create_batch(5)
    
    assert len(todos) == 5
    assert Todo.objects.count() == 5
    
    # すべてのTodoが有効であることを確認
    for todo in todos:
        assert todo.title is not None
        assert todo.created_at is not None
