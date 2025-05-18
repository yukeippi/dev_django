from django.urls import path
from . import views

app_name = 'diary'

urlpatterns = [
    # 日記一覧
    path('', views.DiaryListView.as_view(), name='diary_list'),
    # 日記詳細
    path('<int:pk>/', views.DiaryDetailView.as_view(), name='diary_detail'),
    # 日記作成
    path('create/', views.DiaryCreateView.as_view(), name='diary_create'),
    # 日記編集
    path('<int:pk>/update/', views.DiaryUpdateView.as_view(), name='diary_update'),
    # 日記削除
    path('<int:pk>/delete/', views.DiaryDeleteView.as_view(), name='diary_delete'),
]
