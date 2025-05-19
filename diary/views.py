from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .models import DiaryEntry
from .forms import DiaryEntryForm

# 日記一覧表示
@login_required
def diary_list(request):
    entries = DiaryEntry.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'diary/diary_list.html', {'entries': entries})

# 日記詳細表示
@login_required
def diary_detail(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, author=request.user)
    return render(request, 'diary/diary_detail.html', {'entry': entry})

# 日記作成
@login_required
def diary_create(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            entry.save()
            return redirect('diary_detail', pk=entry.pk)
    else:
        form = DiaryEntryForm()
    return render(request, 'diary/diary_form.html', {'form': form})

# 日記編集
@login_required
def diary_edit(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, author=request.user)
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('diary_detail', pk=entry.pk)
    else:
        form = DiaryEntryForm(instance=entry)
    return render(request, 'diary/diary_form.html', {'form': form})

# 日記削除
@login_required
def diary_delete(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, author=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('diary_list')
    return render(request, 'diary/diary_confirm_delete.html', {'entry': entry})
