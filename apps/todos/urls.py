from django.urls import path
from . import views

app_name = 'todos'

urlpatterns = [
    path('', views.list_view, name='todos_list'),
    path('<int:pk>/', views.detail_view, name='todos_detail'),
    path('create/', views.create_view, name='todos_create'),
    path('edit/<int:pk>/', views.edit_view, name='todos_edit'),
    path('delete/<int:pk>/', views.delete_view, name='todos_delete'),
]
