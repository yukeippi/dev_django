from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import DiaryEntry

class DiaryListView(ListView):
    """日記一覧表示"""
    model = DiaryEntry
    template_name = 'diary/diary_list.html'
    context_object_name = 'diary_entries'
    paginate_by = 10

class DiaryDetailView(DetailView):
    """日記詳細表示"""
    model = DiaryEntry
    template_name = 'diary/diary_detail.html'
    context_object_name = 'diary_entry'

class DiaryCreateView(CreateView):
    """日記作成"""
    model = DiaryEntry
    template_name = 'diary/diary_form.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('diary:diary_list')

    def form_valid(self, form):
        messages.success(self.request, '日記を作成しました。')
        return super().form_valid(form)

class DiaryUpdateView(UpdateView):
    """日記編集"""
    model = DiaryEntry
    template_name = 'diary/diary_form.html'
    fields = ['title', 'content']
    
    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)

class DiaryDeleteView(DeleteView):
    """日記削除"""
    model = DiaryEntry
    template_name = 'diary/diary_confirm_delete.html'
    success_url = reverse_lazy('diary:diary_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '日記を削除しました。')
        return super().delete(request, *args, **kwargs)
