import factory
from django.contrib.auth.models import User
from faker import Faker
from .models import DiaryEntry, DiaryComment

fake = Faker('ja_JP')  # 日本語のダミーデータを生成


class UserFactory(factory.django.DjangoModelFactory):
    """ユーザーファクトリ"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())


class DiaryEntryFactory(factory.django.DjangoModelFactory):
    """日記エントリファクトリ"""
    class Meta:
        model = DiaryEntry
    
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    content = factory.LazyFunction(lambda: fake.text(max_nb_chars=500))
    author = factory.SubFactory(UserFactory)


class DiaryCommentFactory(factory.django.DjangoModelFactory):
    """日記コメントファクトリ"""
    class Meta:
        model = DiaryComment
    
    diary = factory.SubFactory(DiaryEntryFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
