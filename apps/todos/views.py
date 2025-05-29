from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.contrib import messages
from django.core.exceptions import ValidationError

from apps.todos.models import Todo
from apps.todos.forms import TodoForm

class TodoListView(View):
    '''Todo一覧'''
    def get(self, request):
        todos = Todo.objects.all()
        return render(request, 'todos/list.html', {'todos': todos})

class TodoDetailView(View):
    '''Todo詳細'''
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        return render(request, 'todos/detail.html', {'todo': todo})

class TodoEditView(View):
    '''編集画面'''
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        form = TodoForm(instance=todo)
        return render(request, 'todos/edit.html', {
            'form': form,
            'todo': todo
        })

    '''更新処理'''
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
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

list_view = TodoListView.as_view()
detail_view = TodoDetailView.as_view()
edit_view = TodoEditView.as_view()
