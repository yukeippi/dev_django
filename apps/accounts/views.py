from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class LoginView(auth_views.LoginView):
    """ログインビュー"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('todos:todos_list')


class LogoutView(auth_views.LogoutView):
    """ログアウトビュー"""
    next_page = reverse_lazy('accounts:login')


class HomeView(TemplateView):
    """ホームページビュー"""
    template_name = 'accounts/home.html'
