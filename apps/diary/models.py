from django.db import models
from django.utils import timezone

class DiaryEntry(models.Model):
    """日記エントリーモデル"""
    title = models.CharField('タイトル', max_length=200)
    content = models.TextField('内容')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '日記'
        verbose_name_plural = '日記'
        ordering = ['-created_at']  # 新しい順に並べる

    def __str__(self):
        """モデルの文字列表現"""
        return self.title
