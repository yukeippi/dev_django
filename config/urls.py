"""
Django プロジェクトの URL 設定
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('diary.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# 開発環境でのみ有効な設定
if settings.DEBUG:
    # Debug Toolbar
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
    
    # 静的ファイルとメディアファイルの提供
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
