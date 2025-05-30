"""
Playwrightを使用したパスワード再設定機能のE2Eテスト
"""

import asyncio
import re
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from playwright.async_api import async_playwright, Page, Browser


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetPlaywrightE2ETest(StaticLiveServerTestCase):
    """Playwrightを使用したパスワード再設定のE2Eテスト"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = None
        cls.browser = None

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        # テスト用ユーザーを作成
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        # メールボックスをクリア
        mail.outbox.clear()

    async def async_setUp(self):
        """非同期セットアップ"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def async_tearDown(self):
        """非同期クリーンアップ"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def extract_reset_url_from_email(self, email_content):
        """メール本文からパスワード再設定URLを抽出"""
        # URLパターンを検索
        url_pattern = r'http[s]?://[^\s]+/reset/[^/]+/[^/]+/'
        match = re.search(url_pattern, email_content)
        if match:
            return match.group(0)
        return None

    def test_password_reset_complete_flow(self):
        """パスワード再設定の完全なフローをテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # 1. ログインページに移動
                await self.page.goto(f'{self.live_server_url}/login/')
                
                # ページが正しく表示されることを確認
                await self.page.wait_for_selector('h1')
                page_title = await self.page.text_content('h1')
                self.assertIn('ログイン', page_title or '')
                
                # 2. パスワード再設定リンクをクリック
                await self.page.click('text=パスワードを忘れた方はこちら')
                
                # パスワード再設定フォームが表示されることを確認
                await self.page.wait_for_selector('h4:has-text("パスワード再設定")')
                
                # 3. メールアドレスを入力して送信
                await self.page.fill('input[name="email"]', 'test@example.com')
                await self.page.click('button[type="submit"]')
                
                # メール送信完了画面が表示されることを確認
                await self.page.wait_for_selector('h4:has-text("メール送信完了")')
                success_message = await self.page.text_content('h5')
                self.assertIn('パスワード再設定メールを送信しました', success_message or '')
                
                # 4. メールが送信されたことを確認
                self.assertEqual(len(mail.outbox), 1)
                sent_email = mail.outbox[0]
                self.assertEqual(sent_email.to, ['test@example.com'])
                self.assertIn('パスワードリセット', sent_email.subject)
                
                # 5. メールからリセットURLを抽出
                reset_url = self.extract_reset_url_from_email(sent_email.body)
                self.assertIsNotNone(reset_url, "メールからリセットURLを抽出できませんでした")
                
                # 6. リセットURLにアクセス
                if reset_url:
                    await self.page.goto(reset_url)
                else:
                    self.fail("リセットURLが取得できませんでした")
                
                # パスワード設定フォームが表示されることを確認
                await self.page.wait_for_selector('h4:has-text("新しいパスワードの設定")')
                
                # 7. 新しいパスワードを入力
                new_password = 'newpassword123'
                await self.page.fill('input[name="new_password1"]', new_password)
                await self.page.fill('input[name="new_password2"]', new_password)
                
                # パスワード変更ボタンをクリック
                await self.page.click('button[type="submit"]')
                
                # パスワード再設定完了画面が表示されることを確認
                await self.page.wait_for_selector('h4:has-text("パスワード再設定完了")')
                complete_message = await self.page.text_content('h5')
                self.assertIn('パスワードが正常に変更されました', complete_message or '')
                
                # 8. ログインページに移動
                await self.page.click('text=ログインページへ')
                
                # ログインページが表示されることを確認
                await self.page.wait_for_selector('h1:has-text("ログイン")')
                
                # 9. 新しいパスワードでログインを試行
                await self.page.fill('input[name="username"]', 'testuser')
                await self.page.fill('input[name="password"]', new_password)
                await self.page.click('button[type="submit"]')
                
                # ログイン成功を確認（todosページにリダイレクトされる）
                await self.page.wait_for_url('**/todos/**')
                
                # 10. 古いパスワードでログインできないことを確認
                # ログアウト
                await self.page.goto(f'{self.live_server_url}/logout/')
                
                # 再度ログインページに移動
                await self.page.goto(f'{self.live_server_url}/login/')
                
                # 古いパスワードでログインを試行
                await self.page.fill('input[name="username"]', 'testuser')
                await self.page.fill('input[name="password"]', 'oldpassword123')
                await self.page.click('button[type="submit"]')
                
                # ログインエラーが表示されることを確認
                await self.page.wait_for_selector('.alert-error')
                
            finally:
                await self.async_tearDown()
        
        # 非同期テストを実行
        asyncio.run(run_test())

    def test_password_reset_invalid_email(self):
        """存在しないメールアドレスでのパスワード再設定をテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # パスワード再設定ページに移動
                await self.page.goto(f'{self.live_server_url}/password_reset/')
                
                # 存在しないメールアドレスを入力
                await self.page.fill('input[name="email"]', 'nonexistent@example.com')
                await self.page.click('button[type="submit"]')
                
                # メール送信完了画面が表示される（セキュリティのため）
                await self.page.wait_for_selector('h4:has-text("メール送信完了")')
                
                # メールが送信されていないことを確認
                self.assertEqual(len(mail.outbox), 0)
                
            finally:
                await self.async_tearDown()
        
        asyncio.run(run_test())

    def test_password_reset_validation_errors(self):
        """パスワード再設定時のバリデーションエラーをテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # 正常なメールアドレスで送信してリセットURLを取得
                await self.page.goto(f'{self.live_server_url}/password_reset/')
                await self.page.fill('input[name="email"]', 'test@example.com')
                await self.page.click('button[type="submit"]')
                
                await self.page.wait_for_selector('h4:has-text("メール送信完了")')
                
                # メールからリセットURLを取得
                self.assertEqual(len(mail.outbox), 1)
                reset_url = self.extract_reset_url_from_email(mail.outbox[0].body)
                self.assertIsNotNone(reset_url, "メールからリセットURLを抽出できませんでした")
                
                # パスワード確認の不一致をテスト
                if reset_url:
                    await self.page.goto(reset_url)
                else:
                    self.fail("リセットURLが取得できませんでした")
                await self.page.wait_for_selector('h4:has-text("新しいパスワードの設定")')
                
                await self.page.fill('input[name="new_password1"]', 'newpassword123')
                await self.page.fill('input[name="new_password2"]', 'differentpassword')
                await self.page.click('button[type="submit"]')
                
                # エラーメッセージまたはフォームの再表示を確認
                try:
                    await self.page.wait_for_selector('.invalid-feedback', timeout=3000)
                    print("パスワード不一致エラーが表示されました")
                except:
                    # フォームが再表示されていることを確認
                    await self.page.wait_for_selector('h4:has-text("新しいパスワードの設定")', timeout=3000)
                    print("パスワード不一致によりフォームが再表示されました")
                
                # 短すぎるパスワードをテスト
                await self.page.fill('input[name="new_password1"]', '123')
                await self.page.fill('input[name="new_password2"]', '123')
                await self.page.click('button[type="submit"]')
                
                # エラーメッセージまたはフォームの再表示を確認
                try:
                    await self.page.wait_for_selector('.invalid-feedback', timeout=3000)
                    print("短いパスワードエラーが表示されました")
                except:
                    # フォームが再表示されていることを確認
                    await self.page.wait_for_selector('h4:has-text("新しいパスワードの設定")', timeout=3000)
                    print("短いパスワードによりフォームが再表示されました")
                
                # 数字のみのパスワードをテスト
                await self.page.fill('input[name="new_password1"]', '12345678')
                await self.page.fill('input[name="new_password2"]', '12345678')
                await self.page.click('button[type="submit"]')
                
                # エラーメッセージまたはフォームの再表示を確認
                try:
                    await self.page.wait_for_selector('.invalid-feedback', timeout=3000)
                    print("数字のみパスワードエラーが表示されました")
                except:
                    # フォームが再表示されていることを確認
                    await self.page.wait_for_selector('h4:has-text("新しいパスワードの設定")', timeout=3000)
                    print("数字のみパスワードによりフォームが再表示されました")
                
            finally:
                await self.async_tearDown()
        
        asyncio.run(run_test())

    def test_password_reset_invalid_token(self):
        """無効なトークンでのアクセスをテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # 無効なトークンでリセットURLにアクセス
                invalid_url = f'{self.live_server_url}/reset/invalid-uid/invalid-token/'
                await self.page.goto(invalid_url)
                
                # 無効なリンクのメッセージが表示されることを確認
                await self.page.wait_for_selector('h5:has-text("無効なリンクです")')
                
                # 新しい再設定リンクを取得ボタンが表示されることを確認
                await self.page.wait_for_selector('text=新しい再設定リンクを取得')
                
                # ログインページに戻るボタンが表示されることを確認
                await self.page.wait_for_selector('text=ログインページに戻る')
                
            finally:
                await self.async_tearDown()
        
        asyncio.run(run_test())

    def test_password_reset_navigation(self):
        """パスワード再設定フローのナビゲーションをテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # 1. パスワード再設定フォームからログインページに戻る
                await self.page.goto(f'{self.live_server_url}/password_reset/')
                await self.page.click('text=ログインページに戻る')
                
                # ログインページが表示されることを確認
                await self.page.wait_for_selector('h1:has-text("ログイン")')
                
                # 2. メール送信完了画面からログインページに戻る
                await self.page.goto(f'{self.live_server_url}/password_reset/')
                await self.page.fill('input[name="email"]', 'test@example.com')
                await self.page.click('button[type="submit"]')
                
                await self.page.wait_for_selector('h4:has-text("メール送信完了")')
                await self.page.click('text=ログインページに戻る')
                
                # ログインページが表示されることを確認
                await self.page.wait_for_selector('h1:has-text("ログイン")')
                
            finally:
                await self.async_tearDown()
        
        asyncio.run(run_test())

    def test_password_reset_performance(self):
        """パスワード再設定のパフォーマンステスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # パスワード再設定フォームのロード時間を測定
                start_time = asyncio.get_event_loop().time()
                await self.page.goto(f'{self.live_server_url}/password_reset/')
                await self.page.wait_for_load_state('networkidle')
                end_time = asyncio.get_event_loop().time()
                
                load_time = end_time - start_time
                print(f"パスワード再設定フォームのロード時間: {load_time:.2f}秒")
                
                # ページロード時間が3秒以内であることを確認
                self.assertLess(load_time, 3.0)
                
                # メール送信処理の時間を測定
                start_time = asyncio.get_event_loop().time()
                await self.page.fill('input[name="email"]', 'test@example.com')
                await self.page.click('button[type="submit"]')
                await self.page.wait_for_selector('h4:has-text("メール送信完了")')
                end_time = asyncio.get_event_loop().time()
                
                email_send_time = end_time - start_time
                print(f"メール送信処理時間: {email_send_time:.2f}秒")
                
                # メール送信処理が5秒以内であることを確認
                self.assertLess(email_send_time, 5.0)
                
            finally:
                await self.async_tearDown()
        
        asyncio.run(run_test())
