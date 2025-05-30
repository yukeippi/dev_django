from django.urls import path
from . import views
from . import guardian_views
from . import role_views

app_name = 'todos'

urlpatterns = [
    # 通常のTodo機能
    path('', views.list_view, name='todos_list'),
    path('<int:pk>/', views.detail_view, name='todos_detail'),
    path('create/', views.create_view, name='todos_create'),
    path('edit/<int:pk>/', views.edit_view, name='todos_edit'),
    path('delete/<int:pk>/', views.delete_view, name='todos_delete'),
    
    # Guardian権限管理機能
    path('guardian/', guardian_views.guardian_list_view, name='guardian_list'),
    path('guardian/<int:pk>/', guardian_views.guardian_detail_view, name='guardian_detail'),
    path('guardian/create/', guardian_views.guardian_create_view, name='guardian_create'),
    path('guardian/edit/<int:pk>/', guardian_views.guardian_edit_view, name='guardian_edit'),
    path('guardian/delete/<int:pk>/', guardian_views.guardian_delete_view, name='guardian_delete'),
    path('guardian/permissions/<int:pk>/', guardian_views.guardian_permission_view, name='guardian_permissions'),
    
    # ロールベース権限管理機能
    path('role/', role_views.role_list_view, name='role_list'),
    path('role/<int:pk>/', role_views.role_detail_view, name='role_detail'),
    path('role/create/', role_views.role_create_view, name='role_create'),
    path('role/management/<int:pk>/', role_views.role_management_view, name='role_management'),
    path('role/users/', role_views.user_role_management_view, name='user_role_management'),
]
