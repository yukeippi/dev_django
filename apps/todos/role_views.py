"""
Django Guardian を使用したロールベース権限管理のサンプル
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from typing import Dict, List, Any

# Guardian関連のインポート
from guardian.shortcuts import assign_perm, remove_perm, get_perms, get_groups_with_perms
from guardian.core import ObjectPermissionChecker

from apps.todos.models import Todo
from apps.todos.forms import TodoForm


class RoleTodoListView(LoginRequiredMixin, View):
    """ロールベース権限管理付きTodo一覧"""
    
    def get(self, request):
        # ユーザーが属するグループ（ロール）を取得
        user_groups = request.user.groups.all()
        
        # ユーザーが閲覧権限を持つTodoを取得
        checker = ObjectPermissionChecker(request.user)
        todos = []
        
        for todo in Todo.objects.all():
            # 作成者、個人権限、またはグループ権限で閲覧可能
            if (todo.user == request.user or 
                checker.has_perm('view_todo', todo) or
                self._has_group_permission(request.user, todo, 'view_todo')):
                todos.append(todo)
        
        return render(request, 'todos/role_list.html', {
            'todos': todos,
            'user_groups': user_groups,
            'user': request.user
        })
    
    def _has_group_permission(self, user, obj, permission):
        """ユーザーのグループが指定された権限を持つかチェック"""
        groups_with_perms: Dict[Group, List[str]] = get_groups_with_perms(obj, attach_perms=True)  # type: ignore
        user_groups = set(user.groups.all())
        
        for group in user_groups:
            if group in groups_with_perms:
                group_perms = groups_with_perms[group]
                if permission in group_perms:
                    return True
        return False


class RoleTodoDetailView(LoginRequiredMixin, View):
    """ロールベース権限管理付きTodo詳細"""
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 権限チェック
        if not self._can_view_todo(request.user, todo):
            raise PermissionDenied("このTodoを閲覧する権限がありません。")
        
        # ユーザーの個人権限とグループ権限を取得
        user_perms = get_perms(request.user, todo)
        groups_with_perms = get_groups_with_perms(todo, attach_perms=True)
        user_groups = request.user.groups.all()
        
        # ユーザーが持つ実効権限を計算
        groups_with_perms_dict: Dict[Group, List[str]] = groups_with_perms  # type: ignore
        effective_perms = set(user_perms)
        for group in user_groups:
            if group in groups_with_perms_dict:
                group_perms = groups_with_perms_dict[group]
                effective_perms.update(group_perms)
        
        return render(request, 'todos/role_detail.html', {
            'todo': todo,
            'user_perms': user_perms,
            'effective_perms': list(effective_perms),
            'groups_with_perms': groups_with_perms,
            'user_groups': user_groups,
            'is_owner': todo.user == request.user
        })
    
    def _can_view_todo(self, user, todo):
        """Todoの閲覧権限をチェック"""
        if todo.user == user:
            return True
        if user.has_perm('view_todo', todo):
            return True
        
        # グループ権限をチェック
        groups_with_perms: Dict[Group, List[str]] = get_groups_with_perms(todo, attach_perms=True)  # type: ignore
        user_groups = set(user.groups.all())
        
        for group in user_groups:
            if group in groups_with_perms:
                group_perms = groups_with_perms[group]
                if 'view_todo' in group_perms:
                    return True
        
        return False


class RoleTodoCreateView(LoginRequiredMixin, View):
    """ロールベース権限管理付きTodo作成"""
    
    def get(self, request):
        form = TodoForm()
        user_groups = request.user.groups.all()
        return render(request, 'todos/role_create.html', {
            'form': form,
            'user_groups': user_groups
        })
    
    def post(self, request):
        form = TodoForm(request.POST)
        
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            
            # 作成者に個人権限を付与
            assign_perm('view_todo', request.user, todo)
            assign_perm('change_todo', request.user, todo)
            assign_perm('delete_todo', request.user, todo)
            
            # ユーザーが属するグループに基づいて自動権限付与
            self._assign_default_group_permissions(request.user, todo)
            
            messages.success(request, 'Todoが作成され、ロールベース権限が設定されました。')
            return redirect('todos:role_detail', pk=todo.pk)
        
        user_groups = request.user.groups.all()
        return render(request, 'todos/role_create.html', {
            'form': form,
            'user_groups': user_groups
        })
    
    def _assign_default_group_permissions(self, user, todo):
        """ユーザーのロールに基づいてデフォルト権限を付与"""
        for group in user.groups.all():
            if group.name == 'managers':
                # マネージャーグループには全権限
                assign_perm('view_todo', group, todo)
                assign_perm('change_todo', group, todo)
                assign_perm('delete_todo', group, todo)
            elif group.name == 'developers':
                # 開発者グループには閲覧・編集権限
                assign_perm('view_todo', group, todo)
                assign_perm('change_todo', group, todo)
            elif group.name == 'viewers':
                # 閲覧者グループには閲覧権限のみ
                assign_perm('view_todo', group, todo)


class RoleTodoRoleManagementView(LoginRequiredMixin, View):
    """Todoのロール権限管理画面"""
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 作成者のみアクセス可能
        if todo.user != request.user:
            raise PermissionDenied("ロール権限管理は作成者のみ可能です。")
        
        # 全グループと各グループの権限を取得
        all_groups = Group.objects.all()
        groups_with_perms = get_groups_with_perms(todo, attach_perms=True)
        
        groups_with_perms_dict: Dict[Group, List[str]] = groups_with_perms  # type: ignore
        groups_data = []
        for group in all_groups:
            group_perms = groups_with_perms_dict[group] if group in groups_with_perms_dict else []
            groups_data.append({
                'group': group,
                'perms': group_perms,
                'has_view': 'view_todo' in group_perms,
                'has_change': 'change_todo' in group_perms,
                'has_delete': 'delete_todo' in group_perms,
                'member_count': group.user_set.count(),
            })
        
        return render(request, 'todos/role_management.html', {
            'todo': todo,
            'groups_data': groups_data
        })
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        
        # 作成者のみアクセス可能
        if todo.user != request.user:
            raise PermissionDenied("ロール権限管理は作成者のみ可能です。")
        
        group_id = request.POST.get('group_id')
        action = request.POST.get('action')
        permission = request.POST.get('permission')
        
        if group_id and action and permission:
            try:
                group = Group.objects.get(id=group_id)
                
                if action == 'grant':
                    assign_perm(permission, group, todo)
                    messages.success(request, f'{group.name}ロールに{permission}権限を付与しました。')
                elif action == 'revoke':
                    remove_perm(permission, group, todo)
                    messages.success(request, f'{group.name}ロールから{permission}権限を削除しました。')
                
            except Group.DoesNotExist:
                messages.error(request, 'ロールが見つかりません。')
        
        return redirect('todos:role_management', pk=pk)


class RoleManagementView(LoginRequiredMixin, View):
    """ユーザーのロール管理画面"""
    
    def get(self, request):
        # 管理者権限チェック（簡易版）
        if not request.user.is_staff:
            raise PermissionDenied("ロール管理は管理者のみ可能です。")
        
        users = User.objects.all().prefetch_related('groups')
        groups = Group.objects.all()
        
        return render(request, 'todos/user_role_management.html', {
            'users': users,
            'groups': groups
        })
    
    def post(self, request):
        # 管理者権限チェック
        if not request.user.is_staff:
            raise PermissionDenied("ロール管理は管理者のみ可能です。")
        
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        action = request.POST.get('action')
        
        if user_id and group_id and action:
            try:
                user = User.objects.get(id=user_id)
                group = Group.objects.get(id=group_id)
                
                if action == 'add':
                    user.groups.add(group)
                    messages.success(request, f'{user.username}を{group.name}ロールに追加しました。')
                elif action == 'remove':
                    user.groups.remove(group)
                    messages.success(request, f'{user.username}を{group.name}ロールから削除しました。')
                
            except (User.DoesNotExist, Group.DoesNotExist):
                messages.error(request, 'ユーザーまたはロールが見つかりません。')
        
        return redirect('todos:user_role_management')


# ビューのインスタンス化
role_list_view = RoleTodoListView.as_view()
role_detail_view = RoleTodoDetailView.as_view()
role_create_view = RoleTodoCreateView.as_view()
role_management_view = RoleTodoRoleManagementView.as_view()
user_role_management_view = RoleManagementView.as_view()
