from django.apps import AppConfig

class TodosConfig(AppConfig):
    # モデルで主キーが明示的に定義されていない場合のデフォルトフィールドタイプを指定
    default_auto_field = "django.db.models.BigAutoField"
    # アプリケーションの名前を指定
    name = "apps.todos"
