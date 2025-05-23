import pytest
from faker import Faker
from django.contrib.auth.models import User
from diary.models import DiaryEntry

# Fakerのインスタンスを作成（日本語設定）
@pytest.fixture
def faker():
    return Faker('ja_JP')

# テスト用のユーザーを作成するフィクスチャ
@pytest.fixture
def test_user(faker):
    return User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password=faker.password(length=12)
    )

# DiaryEntryを作成するファクトリーフィクスチャ
@pytest.fixture
def diary_factory(test_user, faker):
    def _create_diary(title=None, content=None, author=None):
        return DiaryEntry.objects.create(
            title=title or faker.sentence(nb_words=5),
            content=content or faker.paragraph(nb_sentences=5),  # 十分な長さのテキスト
            author=author or test_user
        )
    return _create_diary

# 有効なDiaryEntryを作成するフィクスチャ
@pytest.fixture
def valid_diary(diary_factory):
    return diary_factory()
