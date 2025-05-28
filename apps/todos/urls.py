from django.urls import path
from . import views

app_name = 'todos'

urlpatterns = [
    path('', views.list_view, name='todos_list'),
    path('<int:pk>/', views.detail_view, name='todos_detail'),
    path('edit/<int:pk>/', views.edit_view, name='todos_edit'),
]
