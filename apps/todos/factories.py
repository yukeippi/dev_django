import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Todo


class TodoFactory(DjangoModelFactory):
    """Todoモデル用のFactory"""
    
    class Meta:
        model = Todo
    
    title = factory.Faker('sentence', nb_words=4, locale='ja_JP')
    description = factory.Faker('text', max_nb_chars=200, locale='ja_JP')
    user = factory.LazyFunction(lambda: User.objects.get_or_create(username='testuser')[0])
    created_at = factory.Faker('date_time_this_year', tzinfo=timezone.get_current_timezone())
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
    completed_at = None


class CompletedTodoFactory(TodoFactory):
    """完了済みTodo用のFactory"""
    
    completed_at = factory.Faker('date_time_this_year', tzinfo=timezone.get_current_timezone())


class IncompleteTodoFactory(TodoFactory):
    """未完了Todo用のFactory"""
    
    completed_at = None


class TodoWithShortDescriptionFactory(TodoFactory):
    """短い説明のTodo用のFactory"""
    
    description = factory.Faker('sentence', nb_words=10, locale='ja_JP')


class TodoWithoutDescriptionFactory(TodoFactory):
    """説明なしTodo用のFactory"""
    
    description = None
