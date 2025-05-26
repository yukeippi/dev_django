from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import DiaryEntry
from .forms import DiaryEntryForm


class DiaryEntryListView(LoginRequiredMixin, ListView):
    """日記一覧表示"""
    model = DiaryEntry
    template_name = 'diary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10
    
    def get_queryset(self):
        # ログインユーザーの日記のみ表示
        return DiaryEntry.objects.filter(author=self.request.user)


class DiaryEntryDetailView(LoginRequiredMixin, DetailView):
    """日記詳細表示"""
    model = DiaryEntry
    template_name = 'diary/entry_detail.html'
    context_object_name = 'entry'
    
    def get_queryset(self):
        # ログインユーザーの日記のみアクセス可能
        return DiaryEntry.objects.filter(author=self.request.user)


class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    """日記作成"""
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'diary/entry_form.html'
    
    def form_valid(self, form):
        # 作成者を自動設定
        form.instance.author = self.request.user
        messages.success(self.request, '日記を作成しました。')
        return super().form_valid(form)


class DiaryEntryUpdateView(LoginRequiredMixin, UpdateView):
    """日記編集"""
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'diary/entry_form.html'
    
    def get_queryset(self):
        # ログインユーザーの日記のみ編集可能
        return DiaryEntry.objects.filter(author=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)


class DiaryEntryDeleteView(LoginRequiredMixin, DeleteView):
    """日記削除"""
    model = DiaryEntry
    template_name = 'diary/entry_confirm_delete.html'
    success_url = reverse_lazy('diary:entry_list')
    
    def get_queryset(self):
        # ログインユーザーの日記のみ削除可能
        return DiaryEntry.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '日記を削除しました。')
        return super().delete(request, *args, **kwargs)
