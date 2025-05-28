from django.shortcuts import render
from django.views.generic import ListView
from django.views import View

from apps.todos.models import Todo

class TodoListView(View):
    def get(self, request):
        todos = Todo.objects.all()
        return render(request, 'todos/list.html', {'todos': todos})

list_view = TodoListView.as_view()
