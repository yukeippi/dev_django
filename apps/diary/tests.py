import pytest
import time
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from apps.diary.models import DiaryEntry


@pytest.fixture
def user():
    """テスト用のユーザーを作成するfixture"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def user2():
    """テスト用の2番目のユーザーを作成するfixture"""
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
def test_create_diary_entry(user):
    """日記エントリーの作成テスト"""
    entry = DiaryEntry.objects.create(
        title='テストタイトル',
        content='テスト内容です。',
        author=user
    )
    
    assert entry.title == 'テストタイトル'
    assert entry.content == 'テスト内容です。'
    assert entry.author == user
    assert entry.is_public is False  # デフォルトはFalse
    assert entry.created_at is not None
    assert entry.updated_at is not None


@pytest.mark.django_db
def test_diary_entry_str_method(user):
    """__str__メソッドのテスト"""
    entry = DiaryEntry.objects.create(
        title='テストタイトル',
        content='テスト内容',
        author=user
    )
    
    expected_str = f"テストタイトル - {entry.created_at.strftime('%Y/%m/%d')}"
    assert str(entry) == expected_str


@pytest.mark.django_db
def test_diary_entry_get_absolute_url(user):
    """get_absolute_urlメソッドのテスト"""
    entry = DiaryEntry.objects.create(
        title='テストタイトル',
        content='テスト内容',
        author=user
    )
    
    expected_url = reverse('diary:entry_detail', kwargs={'pk': entry.pk})
    assert entry.get_absolute_url() == expected_url


@pytest.mark.django_db
def test_diary_entry_ordering(user):
    """エントリーの並び順テスト（新しい順）"""
    # 異なる時間で3つのエントリーを作成
    entry1 = DiaryEntry.objects.create(
        title='最初のエントリー',
        content='内容1',
        author=user
    )
    
    entry2 = DiaryEntry.objects.create(
        title='2番目のエントリー',
        content='内容2',
        author=user
    )
    
    entry3 = DiaryEntry.objects.create(
        title='3番目のエントリー',
        content='内容3',
        author=user
    )
    
    # 新しい順に並んでいることを確認
    entries = DiaryEntry.objects.all()
    assert entries[0] == entry3  # 最新
    assert entries[1] == entry2
    assert entries[2] == entry1  # 最古


@pytest.mark.django_db
def test_diary_entry_public_flag(user):
    """公開フラグのテスト"""
    # デフォルトは非公開
    entry_private = DiaryEntry.objects.create(
        title='非公開エントリー',
        content='非公開内容',
        author=user
    )
    assert entry_private.is_public is False
    
    # 公開エントリー
    entry_public = DiaryEntry.objects.create(
        title='公開エントリー',
        content='公開内容',
        author=user,
        is_public=True
    )
    assert entry_public.is_public is True


@pytest.mark.django_db
def test_diary_entry_author_relationship(user):
    """作成者との関係テスト"""
    entry = DiaryEntry.objects.create(
        title='テストタイトル',
        content='テスト内容',
        author=user
    )
    
    # 作成者が正しく設定されていることを確認
    assert entry.author == user
    assert entry.author.username == 'testuser'
    
    # ユーザーから日記エントリーにアクセスできることを確認
    user_entries = DiaryEntry.objects.filter(author=user)
    assert entry in user_entries


@pytest.mark.django_db
def test_diary_entry_cascade_delete(user):
    """ユーザー削除時のカスケード削除テスト"""
    entry = DiaryEntry.objects.create(
        title='テストタイトル',
        content='テスト内容',
        author=user
    )
    
    entry_id = entry.pk
    
    # ユーザーを削除
    user.delete()
    
    # エントリーも削除されていることを確認
    with pytest.raises(DiaryEntry.DoesNotExist):
        DiaryEntry.objects.get(pk=entry_id)


@pytest.mark.django_db
def test_diary_entry_updated_at_auto_update(user):
    """updated_atの自動更新テスト"""
    entry = DiaryEntry.objects.create(
        title='テストタイトル',
        content='テスト内容',
        author=user
    )
    
    original_updated_at = entry.updated_at
    
    # 少し待ってから更新
    time.sleep(0.1)
    
    entry.title = '更新されたタイトル'
    entry.save()
    
    # updated_atが更新されていることを確認
    entry.refresh_from_db()
    assert entry.updated_at > original_updated_at


@pytest.mark.django_db
def test_diary_entry_title_max_length(user):
    """タイトルの最大長テスト"""
    long_title = 'あ' * 200  # 200文字
    entry = DiaryEntry.objects.create(
        title=long_title,
        content='テスト内容',
        author=user
    )
    assert len(entry.title) == 200
    
    # 201文字は保存時にエラーになることを確認
    very_long_title = 'あ' * 201
    entry_long = DiaryEntry(
        title=very_long_title,
        content='テスト内容',
        author=user
    )
    
    with pytest.raises(ValidationError):
        entry_long.full_clean()


@pytest.mark.django_db
def test_diary_entry_required_fields(user):
    """必須フィールドのテスト"""
    # タイトルなし
    with pytest.raises(ValidationError):
        entry = DiaryEntry(
            content='テスト内容',
            author=user
        )
        entry.full_clean()
    
    # 内容なし
    with pytest.raises(ValidationError):
        entry = DiaryEntry(
            title='テストタイトル',
            author=user
        )
        entry.full_clean()
    
    # 作成者なし
    with pytest.raises(ValidationError):
        entry = DiaryEntry(
            title='テストタイトル',
            content='テスト内容'
        )
        entry.full_clean()


@pytest.mark.django_db
def test_diary_entry_meta_verbose_names():
    """Metaクラスのverbose_nameテスト"""
    meta = DiaryEntry._meta
    assert meta.verbose_name == '日記エントリー'
    assert meta.verbose_name_plural == '日記エントリー'


@pytest.mark.django_db
def test_multiple_entries_per_user(user):
    """1人のユーザーが複数のエントリーを持てることのテスト"""
    entry1 = DiaryEntry.objects.create(
        title='エントリー1',
        content='内容1',
        author=user
    )
    
    entry2 = DiaryEntry.objects.create(
        title='エントリー2',
        content='内容2',
        author=user
    )
    
    user_entries = DiaryEntry.objects.filter(author=user)
    assert user_entries.count() == 2
    assert entry1 in user_entries
    assert entry2 in user_entries


@pytest.mark.django_db
def test_different_users_entries(user, user2):
    """異なるユーザーのエントリーが独立していることのテスト"""
    entry1 = DiaryEntry.objects.create(
        title='ユーザー1のエントリー',
        content='内容1',
        author=user
    )
    
    entry2 = DiaryEntry.objects.create(
        title='ユーザー2のエントリー',
        content='内容2',
        author=user2
    )
    
    user1_entries = DiaryEntry.objects.filter(author=user)
    user2_entries = DiaryEntry.objects.filter(author=user2)
    
    assert user1_entries.count() == 1
    assert user2_entries.count() == 1
    assert entry1 in user1_entries
    assert entry1 not in user2_entries
    assert entry2 in user2_entries
    assert entry2 not in user1_entries


@pytest.mark.django_db
def test_diary_entry_timezone_aware(user):
    """日時フィールドがタイムゾーンを考慮していることのテスト"""
    entry = DiaryEntry.objects.create(
        title='タイムゾーンテスト',
        content='テスト内容',
        author=user
    )
    
    # created_atとupdated_atがタイムゾーンを持っていることを確認
    assert entry.created_at.tzinfo is not None
    assert entry.updated_at.tzinfo is not None
