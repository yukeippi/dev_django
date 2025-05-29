from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError

from apps.todos.models import Todo
from apps.todos.forms import TodoForm

class TodoListView(LoginRequiredMixin, View):
    '''Todo一覧'''
    def get(self, request):
        # ログインユーザーのTodoのみ表示
        todos = Todo.objects.filter(user=request.user)
        return render(request, 'todos/list.html', {'todos': todos})

class TodoDetailView(LoginRequiredMixin, View):
    '''Todo詳細'''
    def get(self, request, pk):
        # ログインユーザーのTodoのみ取得
        todo = get_object_or_404(Todo, pk=pk, user=request.user)
        return render(request, 'todos/detail.html', {'todo': todo})

class TodoCreateView(LoginRequiredMixin, View):
    '''新規作成画面'''
    def get(self, request):
        form = TodoForm()
        return render(request, 'todos/create.html', {'form': form})

    '''新規作成処理'''
    def post(self, request):
        form = TodoForm(request.POST)
        
        if form.is_valid():
            try:
                # モデルのcleanメソッドを呼び出してバリデーション
                todo_instance = form.save(commit=False)
                # ログインユーザーを設定
                todo_instance.user = request.user
                todo_instance.full_clean()
                todo_instance.save()
                messages.success(request, 'Todoが正常に作成されました。')
                return redirect('todos:todos_detail', pk=todo_instance.pk)
            except ValidationError as e:
                # モデルレベルのバリデーションエラーをフォームに追加
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                messages.error(request, 'フォームにエラーがあります。')
                return render(request, 'todos/create.html', {'form': form})
        else:
            messages.error(request, 'フォームにエラーがあります。')
            return render(request, 'todos/create.html', {'form': form})

class TodoEditView(LoginRequiredMixin, View):
    '''編集画面'''
    def get(self, request, pk):
        # ログインユーザーのTodoのみ取得
        todo = get_object_or_404(Todo, pk=pk, user=request.user)
        form = TodoForm(instance=todo)
        return render(request, 'todos/edit.html', {
            'form': form,
            'todo': todo
        })

    '''更新処理'''
    def post(self, request, pk):
        # ログインユーザーのTodoのみ取得
        todo = get_object_or_404(Todo, pk=pk, user=request.user)
        form = TodoForm(request.POST, instance=todo)
        
        if form.is_valid():
            try:
                # モデルのcleanメソッドを呼び出してバリデーション
                todo_instance = form.save(commit=False)
                todo_instance.full_clean()
                todo_instance.save()
                messages.success(request, 'Todoが正常に更新されました。')
                return redirect('todos:todos_detail', pk=todo.pk)
            except ValidationError as e:
                # モデルレベルのバリデーションエラーをフォームに追加
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                messages.error(request, 'フォームにエラーがあります。')
                return render(request, 'todos/edit.html', {
                    'form': form,
                    'todo': todo
                })
        else:
            messages.error(request, 'フォームにエラーがあります。')
            return render(request, 'todos/edit.html', {
                'form': form,
                'todo': todo
            })

class TodoDeleteView(LoginRequiredMixin, View):
    '''削除処理'''
    def post(self, request, pk):
        # ログインユーザーのTodoのみ取得
        todo = get_object_or_404(Todo, pk=pk, user=request.user)
        todo.delete()
        messages.success(request, 'Todoが正常に削除されました。')
        return redirect('todos:todos_list')

list_view = TodoListView.as_view()
detail_view = TodoDetailView.as_view()
create_view = TodoCreateView.as_view()
edit_view = TodoEditView.as_view()
delete_view = TodoDeleteView.as_view()
