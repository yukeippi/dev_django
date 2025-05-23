from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class DiaryEntry(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(
        blank=False,
        null=False,
        validators=[MinLengthValidator(10, message="内容は最低10文字以上入力してください。")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               default=1
                               )
    