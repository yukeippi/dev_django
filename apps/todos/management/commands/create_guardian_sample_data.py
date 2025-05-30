"""
Django Guardian サンプルデータ作成コマンド
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
from apps.todos.models import Todo


class Command(BaseCommand):
    help = 'Guardian権限管理のサンプルデータを作成します'

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
            Todo.objects.filter(user__username__in=['alice', 'bob', 'charlie']).delete()
            # サンプルユーザーを削除
            User.objects.filter(username__in=['alice', 'bob', 'charlie']).delete()

        # サンプルユーザーを作成
        self.stdout.write('サンプルユーザーを作成中...')
        
        alice, created = User.objects.get_or_create(
            username='alice',
            defaults={
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Smith'
            }
        )
        if created:
            alice.set_password('password123')
            alice.save()
            self.stdout.write(f'  ✓ ユーザー作成: {alice.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {alice.username}')

        bob, created = User.objects.get_or_create(
            username='bob',
            defaults={
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Johnson'
            }
        )
        if created:
            bob.set_password('password123')
            bob.save()
            self.stdout.write(f'  ✓ ユーザー作成: {bob.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {bob.username}')

        charlie, created = User.objects.get_or_create(
            username='charlie',
            defaults={
                'email': 'charlie@example.com',
                'first_name': 'Charlie',
                'last_name': 'Brown'
            }
        )
        if created:
            charlie.set_password('password123')
            charlie.save()
            self.stdout.write(f'  ✓ ユーザー作成: {charlie.username}')
        else:
            self.stdout.write(f'  - 既存ユーザー: {charlie.username}')

        # サンプルTodoを作成
        self.stdout.write('\nサンプルTodoを作成中...')

        # Aliceのプライベートなタスク
        todo1, created = Todo.objects.get_or_create(
            title='Aliceの個人的なプロジェクト計画を立てる',
            user=alice,
            defaults={
                'description': 'プライベートなプロジェクトの詳細計画'
            }
        )
        if created:
            # 作成者に全権限を付与
            assign_perm('view_todo', alice, todo1)
            assign_perm('change_todo', alice, todo1)
            assign_perm('delete_todo', alice, todo1)
            self.stdout.write(f'  ✓ Todo作成: {todo1.title}')

        # Aliceのチーム共有タスク
        todo2, created = Todo.objects.get_or_create(
            title='チームミーティングの議事録を作成する',
            user=alice,
            defaults={
                'description': '週次ミーティングの議事録作成'
            }
        )
        if created:
            # 作成者に全権限を付与
            assign_perm('view_todo', alice, todo2)
            assign_perm('change_todo', alice, todo2)
            assign_perm('delete_todo', alice, todo2)
            
            # Bobに閲覧・編集権限を付与
            assign_perm('view_todo', bob, todo2)
            assign_perm('change_todo', bob, todo2)
            
            # Charlieに閲覧権限のみ付与
            assign_perm('view_todo', charlie, todo2)
            
            self.stdout.write(f'  ✓ Todo作成: {todo2.title}')
            self.stdout.write(f'    - Bobに閲覧・編集権限を付与')
            self.stdout.write(f'    - Charlieに閲覧権限を付与')

        # Bobのタスク
        todo3, created = Todo.objects.get_or_create(
            title='データベース設計書を更新する',
            user=bob,
            defaults={
                'description': 'システムのDB設計書を最新版に更新'
            }
        )
        if created:
            # 作成者に全権限を付与
            assign_perm('view_todo', bob, todo3)
            assign_perm('change_todo', bob, todo3)
            assign_perm('delete_todo', bob, todo3)
            
            # Aliceに閲覧権限を付与
            assign_perm('view_todo', alice, todo3)
            
            self.stdout.write(f'  ✓ Todo作成: {todo3.title}')
            self.stdout.write(f'    - Aliceに閲覧権限を付与')

        # Charlieのタスク
        todo4, created = Todo.objects.get_or_create(
            title='テストケースの作成と実行',
            user=charlie,
            defaults={
                'description': '新機能のテストケース作成'
            }
        )
        if created:
            # 作成者に全権限を付与
            assign_perm('view_todo', charlie, todo4)
            assign_perm('change_todo', charlie, todo4)
            assign_perm('delete_todo', charlie, todo4)
            
            # Aliceに全権限を付与（プロジェクトマネージャー的な役割）
            assign_perm('view_todo', alice, todo4)
            assign_perm('change_todo', alice, todo4)
            assign_perm('delete_todo', alice, todo4)
            
            # Bobに閲覧権限を付与
            assign_perm('view_todo', bob, todo4)
            
            self.stdout.write(f'  ✓ Todo作成: {todo4.title}')
            self.stdout.write(f'    - Aliceに全権限を付与')
            self.stdout.write(f'    - Bobに閲覧権限を付与')

        # 共同プロジェクトのタスク
        todo5, created = Todo.objects.get_or_create(
            title='プロジェクト最終報告書の作成',
            user=alice,
            defaults={
                'description': '全員で協力して最終報告書を作成'
            }
        )
        if created:
            # 作成者に全権限を付与
            assign_perm('view_todo', alice, todo5)
            assign_perm('change_todo', alice, todo5)
            assign_perm('delete_todo', alice, todo5)
            
            # 全員に編集権限を付与
            assign_perm('view_todo', bob, todo5)
            assign_perm('change_todo', bob, todo5)
            assign_perm('view_todo', charlie, todo5)
            assign_perm('change_todo', charlie, todo5)
            
            self.stdout.write(f'  ✓ Todo作成: {todo5.title}')
            self.stdout.write(f'    - Bob, Charlieに閲覧・編集権限を付与')

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('サンプルデータの作成が完了しました！'))
        self.stdout.write('\n作成されたユーザー:')
        self.stdout.write(f'  - alice (パスワード: password123)')
        self.stdout.write(f'  - bob (パスワード: password123)')
        self.stdout.write(f'  - charlie (パスワード: password123)')
        
        self.stdout.write('\nアクセス方法:')
        self.stdout.write(f'  1. /admin/ でログインしてユーザーを確認')
        self.stdout.write(f'  2. /todos/guardian/ でGuardian機能を試用')
        self.stdout.write(f'  3. 各ユーザーでログインして権限の違いを確認')
        
        self.stdout.write('\n権限設定の例:')
        self.stdout.write(f'  - Aliceのチーム共有タスク: Bobは編集可、Charlieは閲覧のみ')
        self.stdout.write(f'  - Bobのタスク: Aliceは閲覧のみ')
        self.stdout.write(f'  - Charlieのタスク: Aliceは全権限、Bobは閲覧のみ')
        self.stdout.write(f'  - 共同プロジェクト: 全員が編集可能')
