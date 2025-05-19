from django.urls import path
from . import views

urlpatterns = [
    path('', views.diary_list, name='diary_list'),
    path('entry/<int:pk>/', views.diary_detail, name='diary_detail'),
    path('entry/new/', views.diary_create, name='diary_create'),
    path('entry/<int:pk>/edit/', views.diary_edit, name='diary_edit'),
    path('entry/<int:pk>/delete/', views.diary_delete, name='diary_delete'),
]