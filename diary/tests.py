import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import DiaryEntry

def describe_diary_entry_model():
    """DiaryEntryモデルのテスト"""
    
    @pytest.mark.django_db
    def it_can_create_diary_entry_with_valid_content(test_user, faker):
        """有効なcontentでDiaryEntryが作成できることをテスト"""
        diary = DiaryEntry(
            title=faker.sentence(nb_words=5),
            content=faker.paragraph(nb_sentences=3),  # 十分な長さのテキスト
            author=test_user
        )
        diary.full_clean()  # バリデーションを実行
        diary.save()
        assert DiaryEntry.objects.count() == 1
    
    @pytest.mark.django_db
    def it_cannot_have_empty_content(test_user, faker):
        """contentが空の場合にバリデーションエラーが発生することをテスト"""
        diary = DiaryEntry(
            title=faker.sentence(nb_words=5),
            content="",
            author=test_user
        )
        with pytest.raises(ValidationError):
            diary.full_clean()
    
    @pytest.mark.django_db
    def it_requires_minimum_content_length(test_user, faker):
        """contentが最小長さ未満の場合にバリデーションエラーが発生することをテスト"""
        diary = DiaryEntry(
            title=faker.sentence(nb_words=5),
            content="短すぎる",  # 10文字未満
            author=test_user
        )
        with pytest.raises(ValidationError):
            diary.full_clean()

def describe_diary_entry_factory():
    """DiaryEntryファクトリーのテスト"""
    
    @pytest.mark.django_db
    def it_creates_diary_with_default_values(diary_factory):
        """デフォルト値でDiaryEntryを作成できることをテスト"""
        diary = diary_factory()
        assert diary.title is not None
        assert len(diary.content) >= 10  # 最小長さ以上であることを確認
        assert diary.author is not None
    
    @pytest.mark.django_db
    def it_creates_diary_with_custom_values(diary_factory, test_user, faker):
        """カスタム値でDiaryEntryを作成できることをテスト"""
        custom_title = faker.sentence(nb_words=3)
        custom_content = faker.paragraph(nb_sentences=2)
        
        diary = diary_factory(
            title=custom_title,
            content=custom_content
        )
        
        assert diary.title == custom_title
        assert diary.content == custom_content
        assert diary.author == test_user
    
    @pytest.mark.django_db
    def it_can_use_valid_diary_fixture(valid_diary):
        """valid_diaryフィクスチャを使用できることをテスト"""
        assert valid_diary.id is not None
        assert valid_diary.title is not None
        assert len(valid_diary.content) >= 10  # 最小長さ以上であることを確認
