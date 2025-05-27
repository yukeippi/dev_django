from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from apps.diary.models import DiaryEntry


class DiaryEntryModelTest(TestCase):
    """DiaryEntryモデルのテストクラス"""
    
    def setUp(self):
        """テスト用のデータを準備"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_create_diary_entry(self):
        """日記エントリーの作成テスト"""
        entry = DiaryEntry.objects.create(
            title='テストタイトル',
            content='テスト内容です。',
            author=self.user
        )
        
        self.assertEqual(entry.title, 'テストタイトル')
        self.assertEqual(entry.content, 'テスト内容です。')
        self.assertEqual(entry.author, self.user)
        self.assertFalse(entry.is_public)  # デフォルトはFalse
        self.assertIsNotNone(entry.created_at)
        self.assertIsNotNone(entry.updated_at)
    
    def test_diary_entry_str_method(self):
        """__str__メソッドのテスト"""
        entry = DiaryEntry.objects.create(
            title='テストタイトル',
            content='テスト内容',
            author=self.user
        )
        
        expected_str = f"テストタイトル - {entry.created_at.strftime('%Y/%m/%d')}"
        self.assertEqual(str(entry), expected_str)
    
    def test_diary_entry_get_absolute_url(self):
        """get_absolute_urlメソッドのテスト"""
        entry = DiaryEntry.objects.create(
            title='テストタイトル',
            content='テスト内容',
            author=self.user
        )
        
        expected_url = reverse('diary:entry_detail', kwargs={'pk': entry.pk})
        self.assertEqual(entry.get_absolute_url(), expected_url)
    
    def test_diary_entry_ordering(self):
        """エントリーの並び順テスト（新しい順）"""
        # 異なる時間で3つのエントリーを作成
        entry1 = DiaryEntry.objects.create(
            title='最初のエントリー',
            content='内容1',
            author=self.user
        )
        
        entry2 = DiaryEntry.objects.create(
            title='2番目のエントリー',
            content='内容2',
            author=self.user
        )
        
        entry3 = DiaryEntry.objects.create(
            title='3番目のエントリー',
            content='内容3',
            author=self.user
        )
        
        # 新しい順に並んでいることを確認
        entries = DiaryEntry.objects.all()
        self.assertEqual(entries[0], entry3)  # 最新
        self.assertEqual(entries[1], entry2)
        self.assertEqual(entries[2], entry1)  # 最古
    
    def test_diary_entry_public_flag(self):
        """公開フラグのテスト"""
        # デフォルトは非公開
        entry_private = DiaryEntry.objects.create(
            title='非公開エントリー',
            content='非公開内容',
            author=self.user
        )
        self.assertFalse(entry_private.is_public)
        
        # 公開エントリー
        entry_public = DiaryEntry.objects.create(
            title='公開エントリー',
            content='公開内容',
            author=self.user,
            is_public=True
        )
        self.assertTrue(entry_public.is_public)
    
    def test_diary_entry_author_relationship(self):
        """作成者との関係テスト"""
        entry = DiaryEntry.objects.create(
            title='テストタイトル',
            content='テスト内容',
            author=self.user
        )
        
        # 作成者が正しく設定されていることを確認
        self.assertEqual(entry.author, self.user)
        self.assertEqual(entry.author.username, 'testuser')
        
        # ユーザーから日記エントリーにアクセスできることを確認
        user_entries = DiaryEntry.objects.filter(author=self.user)
        self.assertIn(entry, user_entries)
    
    def test_diary_entry_cascade_delete(self):
        """ユーザー削除時のカスケード削除テスト"""
        entry = DiaryEntry.objects.create(
            title='テストタイトル',
            content='テスト内容',
            author=self.user
        )
        
        entry_id = entry.pk
        
        # ユーザーを削除
        self.user.delete()
        
        # エントリーも削除されていることを確認
        with self.assertRaises(DiaryEntry.DoesNotExist):
            DiaryEntry.objects.get(pk=entry_id)
    
    def test_diary_entry_updated_at_auto_update(self):
        """updated_atの自動更新テスト"""
        entry = DiaryEntry.objects.create(
            title='テストタイトル',
            content='テスト内容',
            author=self.user
        )
        
        original_updated_at = entry.updated_at
        
        # 少し待ってから更新
        import time
        time.sleep(0.1)
        
        entry.title = '更新されたタイトル'
        entry.save()
        
        # updated_atが更新されていることを確認
        entry.refresh_from_db()
        self.assertGreater(entry.updated_at, original_updated_at)
    
    def test_diary_entry_title_max_length(self):
        """タイトルの最大長テスト"""
        long_title = 'あ' * 200  # 200文字
        entry = DiaryEntry.objects.create(
            title=long_title,
            content='テスト内容',
            author=self.user
        )
        self.assertEqual(len(entry.title), 200)
        
        # 201文字は保存時にエラーになることを確認
        very_long_title = 'あ' * 201
        entry_long = DiaryEntry(
            title=very_long_title,
            content='テスト内容',
            author=self.user
        )
        
        with self.assertRaises(ValidationError):
            entry_long.full_clean()
    
    def test_diary_entry_required_fields(self):
        """必須フィールドのテスト"""
        # タイトルなし
        with self.assertRaises(ValidationError):
            entry = DiaryEntry(
                content='テスト内容',
                author=self.user
            )
            entry.full_clean()
        
        # 内容なし
        with self.assertRaises(ValidationError):
            entry = DiaryEntry(
                title='テストタイトル',
                author=self.user
            )
            entry.full_clean()
        
        # 作成者なし
        with self.assertRaises(ValidationError):
            entry = DiaryEntry(
                title='テストタイトル',
                content='テスト内容'
            )
            entry.full_clean()
    
    def test_diary_entry_meta_verbose_names(self):
        """Metaクラスのverbose_nameテスト"""
        meta = DiaryEntry._meta
        self.assertEqual(meta.verbose_name, '日記エントリー')
        self.assertEqual(meta.verbose_name_plural, '日記エントリー')
    
    def test_multiple_entries_per_user(self):
        """1人のユーザーが複数のエントリーを持てることのテスト"""
        entry1 = DiaryEntry.objects.create(
            title='エントリー1',
            content='内容1',
            author=self.user
        )
        
        entry2 = DiaryEntry.objects.create(
            title='エントリー2',
            content='内容2',
            author=self.user
        )
        
        user_entries = DiaryEntry.objects.filter(author=self.user)
        self.assertEqual(user_entries.count(), 2)
        self.assertIn(entry1, user_entries)
        self.assertIn(entry2, user_entries)
    
    def test_different_users_entries(self):
        """異なるユーザーのエントリーが独立していることのテスト"""
        entry1 = DiaryEntry.objects.create(
            title='ユーザー1のエントリー',
            content='内容1',
            author=self.user
        )
        
        entry2 = DiaryEntry.objects.create(
            title='ユーザー2のエントリー',
            content='内容2',
            author=self.user2
        )
        
        user1_entries = DiaryEntry.objects.filter(author=self.user)
        user2_entries = DiaryEntry.objects.filter(author=self.user2)
        
        self.assertEqual(user1_entries.count(), 1)
        self.assertEqual(user2_entries.count(), 1)
        self.assertIn(entry1, user1_entries)
        self.assertNotIn(entry1, user2_entries)
        self.assertIn(entry2, user2_entries)
        self.assertNotIn(entry2, user1_entries)
    
    def test_diary_entry_timezone_aware(self):
        """日時フィールドがタイムゾーンを考慮していることのテスト"""
        entry = DiaryEntry.objects.create(
            title='タイムゾーンテスト',
            content='テスト内容',
            author=self.user
        )
        
        # created_atとupdated_atがタイムゾーンを持っていることを確認
        self.assertIsNotNone(entry.created_at.tzinfo)
        self.assertIsNotNone(entry.updated_at.tzinfo)
