from django.test import TestCase
from django.utils import timezone

from apps.todos.models import Todo
from apps.todos.factories import (
    TodoFactory,
    CompletedTodoFactory,
    IncompleteTodoFactory,
    TodoWithoutDescriptionFactory
)


class TodoModelTest(TestCase):
    """Todoモデルのテストクラス"""

    def setUp(self):
        """テスト用のデータを準備"""
        # Factory Boyを使ってテストデータを作成
        self.todo = TodoFactory(
            title='テストTodo',
            description='これはテスト用のTodoです。'
        )

    def test_create_todo(self):
        """Todoの作成テスト"""
        self.assertEqual(self.todo.title, 'テストTodo')
        self.assertEqual(self.todo.description, 'これはテスト用のTodoです。')
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)
        self.assertIsNone(self.todo.completed_at)

    def test_todo_str_method(self):
        """__str__メソッドのテスト"""
        self.assertEqual(str(self.todo), 'テストTodo')

    def test_todo_ordering(self):
        """Todoの並び順のテスト（Factory Boyを使用）"""
        todos = Todo.objects.all()
        self.assertEqual(todos[0], self.todo)  # 作成したTodoが最初に来るはず
        
        # Factory Boyを使ってさらに2つのTodoを作成
        todo2 = TodoFactory(title='テストTodo2')
        todo3 = TodoFactory(title='テストTodo3')
        
        todos = Todo.objects.all()
        self.assertEqual(todos[0], todo3)
        self.assertEqual(todos[1], todo2)
        self.assertEqual(todos[2], self.todo)

    def test_completed_todo_behavior(self):
        """完了済みTodoの動作テスト"""
        completed_todo = CompletedTodoFactory()
        
        self.assertIsNotNone(completed_todo.completed_at)
        self.assertIsInstance(completed_todo.completed_at, timezone.datetime)

    def test_incomplete_todo_behavior(self):
        """未完了Todoの動作テスト"""
        incomplete_todo = IncompleteTodoFactory()
        
        self.assertIsNone(incomplete_todo.completed_at)

    def test_todo_without_description(self):
        """説明なしTodoの動作テスト"""
        todo_without_desc = TodoWithoutDescriptionFactory()
        
        self.assertIsNone(todo_without_desc.description)
        self.assertIsNotNone(todo_without_desc.title)

    def test_bulk_todo_creation(self):
        """複数のTodoを一括作成するテスト"""
        # 既存のTodoをクリア
        Todo.objects.all().delete()
        
        # Factory Boyを使って複数のTodoを作成
        todos = TodoFactory.create_batch(5)
        
        self.assertEqual(len(todos), 5)
        self.assertEqual(Todo.objects.count(), 5)
        
        # すべてのTodoが有効であることを確認
        for todo in todos:
            self.assertIsNotNone(todo.title)
            self.assertIsNotNone(todo.created_at)
