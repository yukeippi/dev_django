#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # startappコマンドの場合、自動的にappsディレクトリを指定
    if len(sys.argv) >= 3 and sys.argv[1] == 'startapp':
        # 既にディレクトリが指定されていない場合のみappsを追加
        if len(sys.argv) == 3:
            sys.argv.append('apps/')
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
