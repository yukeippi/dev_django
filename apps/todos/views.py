from django.shortcuts import render
from django.views.generic import ListView
from django.views import View

from apps.todos.models import Todo

class TodoListView(View):
    '''Todo一覧'''
    def get(self, request):
        todos = Todo.objects.all()
        return render(request, 'todos/list.html', {'todos': todos})

class TodoDetailView(View):
    '''Todo詳細'''
    def get(self, request, pk):
        todo = Todo.objects.get(pk=pk)
        return render(request, 'todos/detail.html', {'todo': todo})
list_view = TodoListView.as_view()
detail_view = TodoDetailView.as_view()
