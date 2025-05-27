from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    """Todoモデル"""
    
    title = models.CharField('タイトル', max_length=200)
    description = models.TextField('詳細', blank=True, null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='作成者',
        related_name='todos'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    completed_at = models.DateTimeField('完了日時', blank=True, null=True)

    class Meta:
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'
        ordering = ['-created_at']  # 新しい順に並べる

    def __str__(self):
        return self.title
