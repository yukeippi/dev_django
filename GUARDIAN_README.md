# Django Guardian 権限管理サンプル

このプロジェクトでは、django-guardianを使用したオブジェクトレベルの権限管理システムを実装しています。

## 概要

django-guardianは、Djangoの標準権限システムを拡張して、個々のオブジェクトに対する細かい権限制御を可能にするライブラリです。

### 主な機能

- **オブジェクトレベル権限**: 各Todoに対して個別に権限を設定
- **細かい権限制御**: 閲覧・編集・削除権限を個別に管理
- **動的権限管理**: 作成者が他のユーザーに権限を付与・削除
- **権限チェック**: ビューレベルでの権限確認

## インストールと設定

### 1. django-guardianのインストール

```bash
poetry add django-guardian
```

### 2. settings.pyの設定

```python
INSTALLED_APPS = [
    # ...
    'guardian',
    # ...
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # デフォルト
    'guardian.backends.ObjectPermissionBackend',
)

# Guardian設定
GUARDIAN_MONKEY_PATCH_USER = False
```

### 3. マイグレーション実行

```bash
python manage.py migrate
```

## 使用方法

### サンプルデータの作成

```bash
# 新規作成
python manage.py create_guardian_sample_data

# 既存データをリセットして作成
python manage.py create_guardian_sample_data --reset
```

### アクセス方法

1. **Guardian機能**: `/todos/guardian/`
2. **管理画面**: `/admin/`
3. **通常のTodo機能**: `/todos/`

### サンプルユーザー

| ユーザー名 | パスワード | 説明 |
|-----------|-----------|------|
| alice | password123 | プロジェクトマネージャー |
| bob | password123 | 開発者 |
| charlie | password123 | テスター |

## 実装詳細

### 権限の種類

- `view_todo`: Todoの閲覧権限
- `change_todo`: Todoの編集権限
- `delete_todo`: Todoの削除権限

### 主要なファイル

#### ビュー (`apps/todos/guardian_views.py`)

```python
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from guardian.core import ObjectPermissionChecker

# 権限チェックの例
if not request.user.has_perm('change_todo', todo):
    raise PermissionDenied("このTodoを編集する権限がありません。")

# 権限付与の例
assign_perm('view_todo', user, todo)
```

#### URL設定 (`apps/todos/urls.py`)

```python
urlpatterns = [
    # Guardian権限管理機能
    path('guardian/', guardian_views.guardian_list_view, name='guardian_list'),
    path('guardian/<int:pk>/', guardian_views.guardian_detail_view, name='guardian_detail'),
    path('guardian/create/', guardian_views.guardian_create_view, name='guardian_create'),
    path('guardian/edit/<int:pk>/', guardian_views.guardian_edit_view, name='guardian_edit'),
    path('guardian/delete/<int:pk>/', guardian_views.guardian_delete_view, name='guardian_delete'),
    path('guardian/permissions/<int:pk>/', guardian_views.guardian_permission_view, name='guardian_permissions'),
]
```

### 権限管理の流れ

1. **Todo作成時**: 作成者に全権限を自動付与
2. **権限管理画面**: 作成者が他のユーザーに権限を付与/削除
3. **アクセス制御**: 各ビューで権限をチェック
4. **UI表示**: ユーザーの権限に応じてボタンやリンクを表示/非表示

### 権限チェックの実装例

```python
# ビューでの権限チェック
def get(self, request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    
    # 権限チェック
    if todo.user != request.user and not request.user.has_perm('view_todo', todo):
        raise PermissionDenied("このTodoを閲覧する権限がありません。")
    
    return render(request, 'template.html', {'todo': todo})

# テンプレートでの権限チェック
{% if 'change_todo' in user_perms or is_owner %}
    <a href="{% url 'todos:guardian_edit' todo.pk %}" class="btn btn-warning">編集</a>
{% endif %}
```

## 権限設定例

### 基本的な権限パターン

1. **閲覧のみ**: `view_todo`のみ付与
2. **閲覧・編集**: `view_todo` + `change_todo`
3. **フル権限**: `view_todo` + `change_todo` + `delete_todo`

### サンプルデータの権限設定

- **Aliceの個人タスク**: Alice のみ全権限
- **チーム共有タスク**: Alice（全権限）、Bob（閲覧・編集）、Charlie（閲覧のみ）
- **Bobのタスク**: Bob（全権限）、Alice（閲覧のみ）
- **Charlieのタスク**: Charlie（全権限）、Alice（全権限）、Bob（閲覧のみ）
- **共同プロジェクト**: 全員が閲覧・編集可能

## 主要なGuardian機能

### 権限の付与・削除

```python
from guardian.shortcuts import assign_perm, remove_perm

# 権限付与
assign_perm('view_todo', user, todo)
assign_perm('change_todo', user, todo)

# 権限削除
remove_perm('view_todo', user, todo)
```

### 権限の確認

```python
from guardian.shortcuts import get_perms

# ユーザーの権限一覧を取得
user_perms = get_perms(user, todo)

# 特定の権限をチェック
if user.has_perm('change_todo', todo):
    # 編集可能
    pass
```

### 効率的な権限チェック

```python
from guardian.core import ObjectPermissionChecker

# 複数オブジェクトの権限を効率的にチェック
checker = ObjectPermissionChecker(user)
for todo in todos:
    if checker.has_perm('view_todo', todo):
        # 表示対象
        pass
```

## テンプレートでの使用

### 権限に応じた表示制御

```html
<!-- 権限情報の表示 -->
{% if is_owner %}
    <span class="badge bg-primary">作成者</span>
{% else %}
    <span class="badge bg-success">共有</span>
{% endif %}

<!-- 権限に応じたボタン表示 -->
{% if 'change_todo' in user_perms or is_owner %}
    <a href="{% url 'todos:guardian_edit' todo.pk %}" class="btn btn-warning">編集</a>
{% endif %}

{% if 'delete_todo' in user_perms or is_owner %}
    <button type="submit" class="btn btn-danger">削除</button>
{% endif %}
```

## 注意点とベストプラクティス

### セキュリティ

1. **権限チェックの徹底**: すべてのビューで適切な権限チェックを実装
2. **テンプレートでの二重チェック**: ビューとテンプレートの両方で権限確認
3. **作成者権限**: 作成者は常に全権限を持つように設計

### パフォーマンス

1. **ObjectPermissionChecker**: 複数オブジェクトの権限チェック時に使用
2. **select_related/prefetch_related**: 関連オブジェクトの効率的な取得
3. **権限キャッシュ**: 必要に応じて権限情報をキャッシュ

### 設計指針

1. **最小権限の原則**: 必要最小限の権限のみ付与
2. **明示的な権限管理**: 権限の付与・削除を明確に記録
3. **ユーザビリティ**: 権限状況をユーザーに分かりやすく表示

## トラブルシューティング

### よくある問題

1. **権限が反映されない**: マイグレーション実行とサーバー再起動を確認
2. **PermissionDenied例外**: 権限チェックロジックを確認
3. **テンプレートエラー**: 権限変数の存在確認

### デバッグ方法

```python
# 権限の確認
from guardian.shortcuts import get_perms
print(get_perms(user, todo))

# 権限チェッカーの使用
from guardian.core import ObjectPermissionChecker
checker = ObjectPermissionChecker(user)
print(checker.has_perm('view_todo', todo))
```

## ロールベース権限管理（RBAC）

django-guardianは、Djangoの標準Groupモデルを活用してロールベースアクセス制御（RBAC）も実装できます。

### ロールベース機能の特徴

- **グループベース権限**: Groupに権限を付与し、ユーザーをGroupに所属させる
- **階層的権限管理**: ロール（役職）に応じた権限設定
- **効率的な管理**: 個別ユーザーではなくロール単位での権限管理
- **動的ロール変更**: ユーザーのロール変更により権限が自動的に変更

### ロールベースサンプルの使用方法

```bash
# ロールベースサンプルデータの作成
python manage.py create_role_sample_data

# 既存データをリセットして作成
python manage.py create_role_sample_data --reset
```

### アクセス方法

1. **ロールベース機能**: `/todos/role/`
2. **ユーザーロール管理**: `/todos/role/users/` (管理者のみ)

### サンプルロールとユーザー

| ロール | ユーザー | パスワード | 権限レベル |
|--------|----------|-----------|------------|
| managers | manager1 | password123 | 全権限 |
| developers | dev1, dev2 | password123 | 閲覧・編集権限 |
| viewers | viewer1 | password123 | 閲覧権限のみ |

### ロールベース実装のポイント

#### グループ権限の付与

```python
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

# グループに権限を付与
managers_group = Group.objects.get(name='managers')
assign_perm('view_todo', managers_group, todo)
assign_perm('change_todo', managers_group, todo)
assign_perm('delete_todo', managers_group, todo)
```

#### グループ権限のチェック

```python
from guardian.shortcuts import get_groups_with_perms

# オブジェクトに対するグループ権限を取得
groups_with_perms = get_groups_with_perms(todo, attach_perms=True)

# ユーザーのグループ権限をチェック
user_groups = set(user.groups.all())
for group in user_groups:
    group_perms = groups_with_perms.get(group, [])
    if 'view_todo' in group_perms:
        # 閲覧権限あり
        pass
```

#### 実効権限の計算

```python
# ユーザーの個人権限とグループ権限を統合
user_perms = get_perms(user, todo)
effective_perms = set(user_perms)

for group in user.groups.all():
    group_perms = groups_with_perms.get(group, [])
    effective_perms.update(group_perms)
```

### ロールベース vs 個別権限

| 方式 | 適用場面 | メリット | デメリット |
|------|----------|----------|------------|
| **個別権限** | 特定ユーザーへの例外的権限付与 | 細かい制御が可能 | 管理が複雑 |
| **ロールベース** | 組織的な権限管理 | 管理が簡単、スケーラブル | 柔軟性に制限 |
| **ハイブリッド** | 企業システム | 両方の利点を活用 | 実装が複雑 |

### 実装ファイル

- **ビュー**: `apps/todos/role_views.py`
- **URL設定**: ロールベース機能のURL追加
- **サンプルデータ**: `create_role_sample_data` コマンド

## 参考資料

- [django-guardian公式ドキュメント](https://django-guardian.readthedocs.io/)
- [Django権限システム](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)
- [オブジェクトレベル権限の概念](https://django-guardian.readthedocs.io/en/stable/overview.html)
- [Djangoグループとユーザー管理](https://docs.djangoproject.com/en/stable/topics/auth/default/#groups)
