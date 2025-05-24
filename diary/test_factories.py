import pytest
from django.contrib.auth.models import User
from .models import DiaryEntry, DiaryComment
from .factories import UserFactory, DiaryEntryFactory, DiaryCommentFactory


@pytest.mark.django_db
class TestFactories:
    """ファクトリのテストクラス"""
    
    def test_user_factory(self):
        """ユーザーファクトリのテスト"""
        user = UserFactory()
        assert isinstance(user, User)
        assert user.username.startswith('user')
        assert '@example.com' in user.email
        assert user.first_name
        assert user.last_name
    
    def test_diary_entry_factory(self):
        """日記エントリファクトリのテスト"""
        entry = DiaryEntryFactory()
        assert isinstance(entry, DiaryEntry)
        assert entry.title
        assert len(entry.content) >= 10  # バリデーションを満たす
        assert entry.author
        assert entry.created_at
        assert entry.updated_at
    
    def test_diary_comment_factory(self):
        """日記コメントファクトリのテスト"""
        comment = DiaryCommentFactory()
        assert isinstance(comment, DiaryComment)
        assert comment.diary
        assert comment.author
        assert comment.content
        assert comment.created_at
    
    def test_factory_with_custom_attributes(self):
        """カスタム属性を指定したファクトリのテスト"""
        user = UserFactory(username='custom_user')
        entry = DiaryEntryFactory(
            title='カスタムタイトル',
            content='これはカスタムコンテンツです。最低10文字以上必要です。',
            author=user
        )
        
        assert entry.title == 'カスタムタイトル'
        assert entry.author.username == 'custom_user'
    
    def test_factory_batch_creation(self):
        """バッチ作成のテスト"""
        entries = DiaryEntryFactory.create_batch(5)
        assert len(entries) == 5
        assert all(isinstance(entry, DiaryEntry) for entry in entries)
    
    def test_factory_build_without_saving(self):
        """保存せずにオブジェクトを作成するテスト"""
        entry = DiaryEntryFactory.build()
        assert isinstance(entry, DiaryEntry)
        assert entry.pk is None  # まだ保存されていない
        
        # 関連オブジェクト（author）も保存されていない
        assert entry.author.pk is None
        
        # 関連オブジェクトを先に保存してから、エントリを保存
        entry.author.save()
        entry.save()
        assert entry.pk is not None
        assert entry.author.pk is not None


@pytest.mark.django_db
class TestFactoryUsageExamples:
    """ファクトリの実用的な使用例"""
    
    def test_create_diary_with_comments(self):
        """コメント付きの日記を作成する例"""
        # 日記エントリを作成
        entry = DiaryEntryFactory()
        
        # 同じ日記に複数のコメントを作成
        comments = DiaryCommentFactory.create_batch(3, diary=entry)
        
        assert entry.comments.count() == 3
        assert all(comment.diary == entry for comment in comments)
    
    def test_create_user_with_multiple_entries(self):
        """複数の日記を持つユーザーを作成する例"""
        user = UserFactory()
        entries = DiaryEntryFactory.create_batch(5, author=user)
        
        assert DiaryEntry.objects.filter(author=user).count() == 5
        assert all(entry.author == user for entry in entries)
    
    def test_factory_with_traits_simulation(self):
        """特定の特徴を持つオブジェクトの作成例"""
        # 長いコンテンツの日記
        long_entry = DiaryEntryFactory(
            content='これは非常に長いコンテンツです。' * 20
        )
        assert len(long_entry.content) > 100
        
        # 短いタイトルの日記
        short_title_entry = DiaryEntryFactory(title='短いタイトル')
        assert len(short_title_entry.title) < 20
