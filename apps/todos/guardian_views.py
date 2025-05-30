"""
Django Guardian を使用したオブジェクトレベル権限管理のサンプル
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404

# Guardian関連のインポート
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from guardian.decorators import permission_required_or_403
from guardian.mixins import PermissionRequiredMixin
from guardian.core import ObjectPermissionChecker

from apps.todos.models import Todo
from apps.todos.forms import TodoForm


class GuardianTodoListView(LoginRequiredMixin, View):
    """Guardian権限管理付きTodo一覧"""
    
    def get(self, request):
        # ユーザーが閲覧権限を持つTodoのみ表示
        checker = ObjectPermissionChecker(request.user)
        todos = []
        
        for todo in Todo.objects.all():
            # 作成者または閲覧権限を持つユーザーのみ表示
            if todo.user == request.user or checker.has_perm('view_todo', todo):
                todos.append(todo)
        
        return render(request, 'todos/guardian_list.html', {
            'todos': todos,
            'user': request.user
        })


class GuardianTodoDetailView(LoginRequiredMixin, View):
    """Guardian権限管理付きTodo詳細"""
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 権限チェック：作成者または閲覧権限を持つユーザーのみアクセス可能
        if todo.user != request.user and not request.user.has_perm('view_todo', todo):
            raise PermissionDenied("このTodoを閲覧する権限がありません。")
        
        # ユーザーの権限情報を取得
        user_perms = get_perms(request.user, todo)
        
        return render(request, 'todos/guardian_detail.html', {
            'todo': todo,
            'user_perms': user_perms,
            'is_owner': todo.user == request.user
        })


class GuardianTodoCreateView(LoginRequiredMixin, View):
    """Guardian権限管理付きTodo作成"""
    
    def get(self, request):
        form = TodoForm()
        return render(request, 'todos/guardian_create.html', {'form': form})
    
    def post(self, request):
        form = TodoForm(request.POST)
        
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            
            # 作成者に全権限を付与
            assign_perm('view_todo', request.user, todo)
            assign_perm('change_todo', request.user, todo)
            assign_perm('delete_todo', request.user, todo)
            
            messages.success(request, 'Todoが作成され、権限が設定されました。')
            return redirect('todos:guardian_detail', pk=todo.pk)
        
        return render(request, 'todos/guardian_create.html', {'form': form})


class GuardianTodoEditView(LoginRequiredMixin, View):
    """Guardian権限管理付きTodo編集"""
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 編集権限チェック
        if not request.user.has_perm('change_todo', todo):
            raise PermissionDenied("このTodoを編集する権限がありません。")
        
        form = TodoForm(instance=todo)
        return render(request, 'todos/guardian_edit.html', {
            'form': form,
            'todo': todo
        })
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 編集権限チェック
        if not request.user.has_perm('change_todo', todo):
            raise PermissionDenied("このTodoを編集する権限がありません。")
        
        form = TodoForm(request.POST, instance=todo)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Todoが更新されました。')
            return redirect('todos:guardian_detail', pk=todo.pk)
        
        return render(request, 'todos/guardian_edit.html', {
            'form': form,
            'todo': todo
        })


class GuardianTodoDeleteView(LoginRequiredMixin, View):
    """Guardian権限管理付きTodo削除"""
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 削除権限チェック
        if not request.user.has_perm('delete_todo', todo):
            raise PermissionDenied("このTodoを削除する権限がありません。")
        
        todo.delete()
        messages.success(request, 'Todoが削除されました。')
        return redirect('todos:guardian_list')


class GuardianTodoPermissionView(LoginRequiredMixin, View):
    """Todo権限管理画面"""
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 作成者のみアクセス可能
        if todo.user != request.user:
            raise PermissionDenied("権限管理は作成者のみ可能です。")
        
        # 全ユーザーと各ユーザーの権限を取得
        users_with_perms = []
        for user in User.objects.exclude(id=request.user.id):
            user_perms = get_perms(user, todo)
            users_with_perms.append({
                'user': user,
                'perms': user_perms,
                'has_view': 'view_todo' in user_perms,
                'has_change': 'change_todo' in user_perms,
                'has_delete': 'delete_todo' in user_perms,
            })
        
        return render(request, 'todos/guardian_permissions.html', {
            'todo': todo,
            'users_with_perms': users_with_perms
        })
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 作成者のみアクセス可能
        if todo.user != request.user:
            raise PermissionDenied("権限管理は作成者のみ可能です。")
        
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        permission = request.POST.get('permission')
        
        if user_id and action and permission:
            try:
                target_user = User.objects.get(id=user_id)
                
                if action == 'grant':
                    assign_perm(permission, target_user, todo)
                    messages.success(request, f'{target_user.username}に{permission}権限を付与しました。')
                elif action == 'revoke':
                    remove_perm(permission, target_user, todo)
                    messages.success(request, f'{target_user.username}から{permission}権限を削除しました。')
                
            except User.DoesNotExist:
                messages.error(request, 'ユーザーが見つかりません。')
        
        return redirect('todos:guardian_permissions', pk=pk)


# ビューのインスタンス化
guardian_list_view = GuardianTodoListView.as_view()
guardian_detail_view = GuardianTodoDetailView.as_view()
guardian_create_view = GuardianTodoCreateView.as_view()
guardian_edit_view = GuardianTodoEditView.as_view()
guardian_delete_view = GuardianTodoDeleteView.as_view()
guardian_permission_view = GuardianTodoPermissionView.as_view()
