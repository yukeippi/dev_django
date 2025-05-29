#!/usr/bin/env python
"""
E2Eテスト実行スクリプト（Playwright版）
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_environment():
    """テスト環境をセットアップ"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.test_settings')
    
    # Djangoの設定を初期化
    import django
    django.setup()

def install_playwright_browsers():
    """Playwrightブラウザをインストール"""
    print("Playwrightブラウザをインストール中...")
    try:
        subprocess.run(['playwright', 'install', 'chromium'], check=True)
        print("Playwrightブラウザのインストールが完了しました。")
    except subprocess.CalledProcessError as e:
        print(f"Playwrightブラウザのインストールに失敗しました: {e}")
        return False
    except FileNotFoundError:
        print("Playwrightが見つかりません。poetry installを実行してください。")
        return False
    return True

def run_e2e_tests():
    """E2Eテストを実行"""
    print("\n=== E2Eテストを実行中 ===")
    cmd = [
        'python', 'manage.py', 'test', 
        'apps.todos.test_e2e_playwright',
        '--settings=config.test_settings',
        '--verbosity=2'
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("E2Eテストが正常に完了しました。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"E2Eテストが失敗しました: {e}")
        return False

def check_dependencies():
    """依存関係をチェック"""
    print("依存関係をチェック中...")
    
    try:
        import playwright
        print("✓ Playwright インストール済み")
    except ImportError:
        print("✗ Playwrightがインストールされていません")
        return False
    
    try:
        import django
        print(f"✓ Django {django.__version__}")
    except ImportError:
        print("✗ Djangoがインストールされていません")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='E2Eテスト実行スクリプト（Playwright版）')
    parser.add_argument(
        '--install-browsers', 
        action='store_true',
        help='Playwrightブラウザをインストール'
    )
    parser.add_argument(
        '--check-deps', 
        action='store_true',
        help='依存関係をチェック'
    )
    
    args = parser.parse_args()
    
    # 依存関係チェック
    if args.check_deps:
        if not check_dependencies():
            sys.exit(1)
        return
    
    # 環境セットアップ
    setup_environment()
    
    # Playwrightブラウザインストール
    if args.install_browsers:
        if not install_playwright_browsers():
            sys.exit(1)
        return
    
    # Playwrightブラウザが必要
    if not install_playwright_browsers():
        sys.exit(1)
    
    # テスト実行
    success = run_e2e_tests()
    
    if not success:
        sys.exit(1)
    
    print("\n🎉 E2Eテストが正常に完了しました！")

if __name__ == '__main__':
    main()
