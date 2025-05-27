from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class DiaryEntry(models.Model):
    title = models.CharField('タイトル', max_length=200)
    content = models.TextField('内容')
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='作成者',
        related_name='diary_entries'
    )
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    is_public = models.BooleanField('公開', default=False)
    
    class Meta:
        verbose_name = '日記エントリー'
        verbose_name_plural = '日記エントリー'
        ordering = ['-created_at']  # 新しい順に並べる
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y/%m/%d')}"
    
    def get_absolute_url(self):
        return reverse('diary:entry_detail', kwargs={'pk': self.pk})
