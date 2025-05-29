from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    title = forms.CharField(
        label='タイトル',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'タスクのタイトルを入力してください'
        })
    )
    description = forms.CharField(
        label='説明',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'タスクの詳細を入力してください...'
        })
    )
    
    class Meta:
        model = Todo
        fields = ['title', 'description']
