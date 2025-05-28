from django.urls import path
from . import views

app_name = 'todos'

urlpatterns = [
    path('', views.list_view, name='todos_list'),
]
