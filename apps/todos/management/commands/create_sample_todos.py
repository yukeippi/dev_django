from django.core.management.base import BaseCommand
from apps.todos.factories import (
    TodoFactory,
    CompletedTodoFactory,
    IncompleteTodoFactory,
    TodoWithoutDescriptionFactory
)
from apps.todos.models import Todo


class Command(BaseCommand):
    help = 'Factory Boyを使ってサンプルTodoデータを作成します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='作成するTodoの数（デフォルト: 10）'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='既存のTodoデータを削除してから作成'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        if options['clear']:
            Todo.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('既存のTodoデータを削除しました。')
            )

        # 様々なタイプのTodoを作成
        self.stdout.write('サンプルTodoデータを作成中...')
        
        # 通常のTodo
        normal_todos = TodoFactory.create_batch(count // 2)
        self.stdout.write(f'通常のTodo: {len(normal_todos)}件作成')
        
        # 完了済みTodo
        completed_todos = CompletedTodoFactory.create_batch(count // 4)
        self.stdout.write(f'完了済みTodo: {len(completed_todos)}件作成')
        
        # 説明なしTodo
        no_desc_todos = TodoWithoutDescriptionFactory.create_batch(count // 4)
        self.stdout.write(f'説明なしTodo: {len(no_desc_todos)}件作成')
        
        total_created = len(normal_todos) + len(completed_todos) + len(no_desc_todos)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'合計 {total_created}件のサンプルTodoデータを作成しました。'
            )
        )
        
        # 統計情報を表示
        total_todos = Todo.objects.count()
        completed_count = Todo.objects.filter(completed_at__isnull=False).count()
        incomplete_count = Todo.objects.filter(completed_at__isnull=True).count()
        no_description_count = Todo.objects.filter(description__isnull=True).count()
        
        self.stdout.write('\n=== 現在のTodo統計 ===')
        self.stdout.write(f'総Todo数: {total_todos}')
        self.stdout.write(f'完了済み: {completed_count}')
        self.stdout.write(f'未完了: {incomplete_count}')
        self.stdout.write(f'説明なし: {no_description_count}')
