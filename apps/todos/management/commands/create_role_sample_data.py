"""
Django Guardian ロールベース権限管理のサンプルデータ作成コマンド
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from guardian.shortcuts import assign_perm
from apps.todos.models import Todo


class Command(BaseCommand):
    help = 'Guardian ロールベース権限管理のサンプルデータを作成します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='既存のサンプルデータを削除してから作成',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('既存のサンプルデータを削除中...')
            # サンプルユーザーのTodoを削除
            Todo.objects.filter(user__username__in=['manager1', 'dev1', 'dev2', 'viewer1']).delete()
            # サンプルユーザーを削除
            User.objects.filter(username__in=['manager1', 'dev1', 'dev2', 'viewer1']).delete()
            # サンプルグループを削除
            Group.objects.filter(name__in=['managers', 'developers', 'viewers']).delete()

        # ロール（グループ）を作成
        self.stdout.write('ロール（グループ）を作成中...')
        
        managers_group, created = Group.objects.get_or_create(name='managers')
        if created:
            self.stdout.write(f'  ✓ ロール作成: {managers_group.name}')
        else:
            self.stdout.write(f'  - 既存ロール: {managers_group.name}')

        developers_group, created = Group.objects.get_or_create(name='developers')
        if created:
            self.stdout.write(f'  ✓ ロール作成: {developers_group.name}')
        else:
            self.stdout.write(f'  - 既存ロール: {developers_group.name}')

        viewers_group, created = Group.objects.get_or_create(name='viewers')
        if created:
            self.stdout.write(f'  ✓ ロール作成: {viewers_group.name}')
        else:
            self.stdout.write(f'  - 既存ロール: {viewers_group.name}')

        # サンプルユーザーを作成
        self.stdout.write('\nサンプルユーザーを作成中...')
        
        # マネージャー
        manager1, created = User.objects.get_or_create(
            username='manager1',
            defaults={
                'email': 'manager1@example.com',
                'first_name': 'Manager',
                'last_name': 'One',
                'is_staff': True
            }
        )
        if created:
            manager1.set_password('password123')
            manager1.save()
            self.stdout.write(f'  ✓ ユーザー作成: {manager1.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {manager1.username}')
        
        manager1.groups.add(managers_group)

        # 開発者1
        dev1, created = User.objects.get_or_create(
            username='dev1',
            defaults={
                'email': 'dev1@example.com',
                'first_name': 'Developer',
                'last_name': 'One'
            }
        )
        if created:
            dev1.set_password('password123')
            dev1.save()
            self.stdout.write(f'  ✓ ユーザー作成: {dev1.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {dev1.username}')
        
        dev1.groups.add(developers_group)

        # 開発者2
        dev2, created = User.objects.get_or_create(
            username='dev2',
            defaults={
                'email': 'dev2@example.com',
                'first_name': 'Developer',
                'last_name': 'Two'
            }
        )
        if created:
            dev2.set_password('password123')
            dev2.save()
            self.stdout.write(f'  ✓ ユーザー作成: {dev2.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {dev2.username}')
        
        dev2.groups.add(developers_group)

        # 閲覧者
        viewer1, created = User.objects.get_or_create(
            username='viewer1',
            defaults={
                'email': 'viewer1@example.com',
                'first_name': 'Viewer',
                'last_name': 'One'
            }
        )
        if created:
            viewer1.set_password('password123')
            viewer1.save()
            self.stdout.write(f'  ✓ ユーザー作成: {viewer1.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {viewer1.username}')
        
        viewer1.groups.add(viewers_group)

        # サンプルTodoを作成
        self.stdout.write('\nサンプルTodoを作成中...')

        # マネージャーのプロジェクト管理タスク
        todo1, created = Todo.objects.get_or_create(
            title='プロジェクト全体の進捗管理と調整',
            user=manager1,
            defaults={
                'description': 'チーム全体の進捗確認と課題解決'
            }
        )
        if created:
            # 作成者に個人権限を付与
            assign_perm('view_todo', manager1, todo1)
            assign_perm('change_todo', manager1, todo1)
            assign_perm('delete_todo', manager1, todo1)
            
            # 開発者グループに閲覧・編集権限を付与
            assign_perm('view_todo', developers_group, todo1)
            assign_perm('change_todo', developers_group, todo1)
            
            # 閲覧者グループに閲覧権限を付与
            assign_perm('view_todo', viewers_group, todo1)
            
            self.stdout.write(f'  ✓ Todo作成: {todo1.title}')
            self.stdout.write(f'    - developersグループに閲覧・編集権限を付与')
            self.stdout.write(f'    - viewersグループに閲覧権限を付与')

        # 開発者1のタスク
        todo2, created = Todo.objects.get_or_create(
            title='ユーザー認証機能の実装',
            user=dev1,
            defaults={
                'description': 'ログイン・ログアウト機能の開発'
            }
        )
        if created:
            # 作成者に個人権限を付与
            assign_perm('view_todo', dev1, todo2)
            assign_perm('change_todo', dev1, todo2)
            assign_perm('delete_todo', dev1, todo2)
            
            # マネージャーグループに全権限を付与
            assign_perm('view_todo', managers_group, todo2)
            assign_perm('change_todo', managers_group, todo2)
            assign_perm('delete_todo', managers_group, todo2)
            
            # 他の開発者に閲覧権限を付与
            assign_perm('view_todo', developers_group, todo2)
            
            self.stdout.write(f'  ✓ Todo作成: {todo2.title}')
            self.stdout.write(f'    - managersグループに全権限を付与')
            self.stdout.write(f'    - developersグループに閲覧権限を付与')

        # 開発者2のタスク
        todo3, created = Todo.objects.get_or_create(
            title='データベース設計とマイグレーション',
            user=dev2,
            defaults={
                'description': 'DB設計書作成とマイグレーションファイル作成'
            }
        )
        if created:
            # 作成者に個人権限を付与
            assign_perm('view_todo', dev2, todo3)
            assign_perm('change_todo', dev2, todo3)
            assign_perm('delete_todo', dev2, todo3)
            
            # マネージャーグループに全権限を付与
            assign_perm('view_todo', managers_group, todo3)
            assign_perm('change_todo', managers_group, todo3)
            assign_perm('delete_todo', managers_group, todo3)
            
            # 開発者グループに閲覧・編集権限を付与
            assign_perm('view_todo', developers_group, todo3)
            assign_perm('change_todo', developers_group, todo3)
            
            self.stdout.write(f'  ✓ Todo作成: {todo3.title}')
            self.stdout.write(f'    - managersグループに全権限を付与')
            self.stdout.write(f'    - developersグループに閲覧・編集権限を付与')

        # 共同作業タスク
        todo4, created = Todo.objects.get_or_create(
            title='システム統合テストの実施',
            user=manager1,
            defaults={
                'description': '全機能の統合テストとバグ修正'
            }
        )
        if created:
            # 作成者に個人権限を付与
            assign_perm('view_todo', manager1, todo4)
            assign_perm('change_todo', manager1, todo4)
            assign_perm('delete_todo', manager1, todo4)
            
            # 全グループに適切な権限を付与
            assign_perm('view_todo', managers_group, todo4)
            assign_perm('change_todo', managers_group, todo4)
            assign_perm('delete_todo', managers_group, todo4)
            
            assign_perm('view_todo', developers_group, todo4)
            assign_perm('change_todo', developers_group, todo4)
            
            assign_perm('view_todo', viewers_group, todo4)
            
            self.stdout.write(f'  ✓ Todo作成: {todo4.title}')
            self.stdout.write(f'    - 全グループに適切な権限を付与')

        # 閲覧専用タスク
        todo5, created = Todo.objects.get_or_create(
            title='プロジェクト仕様書の確認',
            user=viewer1,
            defaults={
                'description': '仕様書の内容確認と質問事項の整理'
            }
        )
        if created:
            # 作成者に個人権限を付与
            assign_perm('view_todo', viewer1, todo5)
            assign_perm('change_todo', viewer1, todo5)
            assign_perm('delete_todo', viewer1, todo5)
            
            # マネージャーと開発者に閲覧権限を付与
            assign_perm('view_todo', managers_group, todo5)
            assign_perm('view_todo', developers_group, todo5)
            
            self.stdout.write(f'  ✓ Todo作成: {todo5.title}')
            self.stdout.write(f'    - managers, developersグループに閲覧権限を付与')

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ロールベースサンプルデータの作成が完了しました！'))
        
        self.stdout.write('\n作成されたロール:')
        self.stdout.write(f'  - managers: プロジェクト管理者（全権限）')
        self.stdout.write(f'  - developers: 開発者（閲覧・編集権限）')
        self.stdout.write(f'  - viewers: 閲覧者（閲覧権限のみ）')
        
        self.stdout.write('\n作成されたユーザー:')
        self.stdout.write(f'  - manager1 (パスワード: password123) - managersロール')
        self.stdout.write(f'  - dev1 (パスワード: password123) - developersロール')
        self.stdout.write(f'  - dev2 (パスワード: password123) - developersロール')
        self.stdout.write(f'  - viewer1 (パスワード: password123) - viewersロール')
        
        self.stdout.write('\nアクセス方法:')
        self.stdout.write(f'  1. /admin/ でログインしてロールを確認')
        self.stdout.write(f'  2. /todos/role/ でロールベース機能を試用')
        self.stdout.write(f'  3. 各ユーザーでログインしてロール権限の違いを確認')
        
        self.stdout.write('\nロール権限の例:')
        self.stdout.write(f'  - マネージャー: 全Todoに対して全権限')
        self.stdout.write(f'  - 開発者: 開発関連Todoの閲覧・編集権限')
        self.stdout.write(f'  - 閲覧者: 指定されたTodoの閲覧権限のみ')
