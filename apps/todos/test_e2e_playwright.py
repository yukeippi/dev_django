"""
Playwrightを使用したTodoアプリのE2Eテスト
"""

import asyncio
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from playwright.async_api import async_playwright, Page, Browser


class TodoPlaywrightE2ETest(StaticLiveServerTestCase):
    """Playwrightを使用したTodoのE2Eテスト"""

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
            password='testpass123'
        )

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

    async def login(self, username='testuser', password='testpass123'):
        """ユーザーログイン"""
        await self.page.goto(f'{self.live_server_url}/login/')
        
        # ユーザー名とパスワードを入力
        await self.page.fill('input[name="username"]', username)
        await self.page.fill('input[name="password"]', password)
        
        # ログインボタンをクリック
        await self.page.click('button[type="submit"]')
        
        # ログイン成功を確認（todosページにリダイレクトされる）
        await self.page.wait_for_url('**/todos/**')

    def test_todo_crud_flow_playwright(self):
        """PlaywrightでTodo CRUD操作の一連の流れをテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # 1. ログイン
                await self.login()
                
                # 2. Todo一覧ページに移動
                await self.page.goto(f'{self.live_server_url}/todos/')
                
                # 一覧ページが表示されることを確認
                await self.page.wait_for_selector('h1')
                page_title = await self.page.text_content('h1')
                self.assertIn('Todo', page_title or '')
                
                # 3. Todo作成ページに移動
                await self.page.click('text=新規作成')
                
                # 作成ページが表示されることを確認
                await self.page.wait_for_selector('#id_title')
                
                # 4. Todoを作成
                test_title = 'Playwrightテスト用のTodoタイトル'
                test_description = 'Playwrightテスト用の説明'
                
                await self.page.fill('#id_title', test_title)
                await self.page.fill('#id_description', test_description)
                
                # 作成ボタンをクリック
                await self.page.click('input[type="submit"]')
                
                # 詳細ページにリダイレクトされることを確認
                await self.page.wait_for_selector(f'h1:has-text("{test_title}")')
                
                # 作成されたTodoの詳細が表示されることを確認
                detail_title = await self.page.text_content('h1')
                self.assertEqual(detail_title or '', test_title)
                
                # 5. Todo編集ページに移動
                await self.page.click('text=編集')
                
                # 編集ページが表示されることを確認
                await self.page.wait_for_selector('#id_title')
                
                # 6. Todoを編集
                updated_title = 'Playwrightテスト用の更新されたTodoタイトル'
                updated_description = 'Playwrightテスト用の更新された説明'
                
                await self.page.fill('#id_title', updated_title)
                await self.page.fill('#id_description', updated_description)
                
                # 更新ボタンをクリック
                await self.page.click('input[type="submit"]')
                
                # 詳細ページにリダイレクトされることを確認
                await self.page.wait_for_selector(f'h1:has-text("{updated_title}")')
                
                # 更新されたTodoの詳細が表示されることを確認
                detail_title = await self.page.text_content('h1')
                self.assertEqual(detail_title or '', updated_title)
                
                # 7. Todo一覧ページに戻る
                await self.page.click('text=一覧')
                
                # 一覧ページで更新されたTodoが表示されることを確認
                await self.page.wait_for_selector(f'text={updated_title}')
                
                # 8. Todoを削除
                # 詳細ページに戻る
                await self.page.click(f'text={updated_title}')
                
                # 確認ダイアログを処理するためのリスナーを設定
                self.page.on('dialog', lambda dialog: dialog.accept())
                
                # 削除ボタンをクリック
                await self.page.click('input[value="削除"]')
                
                # 一覧ページにリダイレクトされることを確認
                await self.page.wait_for_selector('h1')
                
                # 削除されたTodoが一覧に表示されないことを確認
                page_content = await self.page.content()
                self.assertNotIn(updated_title, page_content)
                
            finally:
                await self.async_tearDown()
        
        # 非同期テストを実行
        asyncio.run(run_test())

    def test_todo_validation_errors_playwright(self):
        """Playwrightでバリデーションエラーをテスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # ログイン
                await self.login()
                
                # Todo作成ページに移動
                await self.page.goto(f'{self.live_server_url}/todos/create/')
                
                # 1. 空のフォームを送信
                await self.page.click('input[type="submit"]')
                
                # エラーメッセージが表示されることを確認
                await self.page.wait_for_selector('.invalid-feedback')
                error_elements = await self.page.query_selector_all('.invalid-feedback')
                self.assertTrue(len(error_elements) > 0)
                
                # 2. タイトルが短すぎる場合
                await self.page.fill('#id_title', '短い')  # 10文字未満
                await self.page.click('input[type="submit"]')
                
                # バリデーションエラーが表示されることを確認
                await self.page.wait_for_selector('.invalid-feedback')
                
                # 3. 説明が長すぎる場合
                await self.page.fill('#id_title', 'Playwrightテスト用の有効なタイトル')
                
                # 30文字以上の説明を入力
                long_description = 'これは30文字を超える非常に長い説明文です。バリデーションエラーが発生するはずです。'
                await self.page.fill('#id_description', long_description)
                
                await self.page.click('input[type="submit"]')
                
                # バリデーションエラーが表示されることを確認
                await self.page.wait_for_selector('.invalid-feedback')
                
            finally:
                await self.async_tearDown()
        
        # 非同期テストを実行
        asyncio.run(run_test())

    def test_todo_performance_playwright(self):
        """Playwrightでパフォーマンステスト"""
        
        async def run_test():
            await self.async_setUp()
            
            try:
                # ログイン
                await self.login()
                
                # ページロード時間を測定
                start_time = asyncio.get_event_loop().time()
                await self.page.goto(f'{self.live_server_url}/todos/')
                await self.page.wait_for_load_state('networkidle')
                end_time = asyncio.get_event_loop().time()
                
                load_time = end_time - start_time
                print(f"Todo一覧ページのロード時間: {load_time:.2f}秒")
                
                # ページロード時間が5秒以内であることを確認
                self.assertLess(load_time, 5.0)
                
                # 複数のTodoを作成してパフォーマンスをテスト
                for i in range(5):
                    await self.page.goto(f'{self.live_server_url}/todos/create/')
                    await self.page.fill('#id_title', f'パフォーマンステスト用Todo {i+1}')
                    await self.page.fill('#id_description', f'説明 {i+1}')
                    
                    start_time = asyncio.get_event_loop().time()
                    await self.page.click('input[type="submit"]')
                    await self.page.wait_for_selector('h1')
                    end_time = asyncio.get_event_loop().time()
                    
                    create_time = end_time - start_time
                    print(f"Todo作成時間 {i+1}: {create_time:.2f}秒")
                    
                    # 作成時間が3秒以内であることを確認
                    self.assertLess(create_time, 3.0)
                
                # 一覧ページのロード時間を再測定
                start_time = asyncio.get_event_loop().time()
                await self.page.goto(f'{self.live_server_url}/todos/')
                await self.page.wait_for_load_state('networkidle')
                end_time = asyncio.get_event_loop().time()
                
                list_load_time = end_time - start_time
                print(f"Todo一覧ページ（5件）のロード時間: {list_load_time:.2f}秒")
                
                # 5件のTodoがある状態でも5秒以内でロードできることを確認
                self.assertLess(list_load_time, 5.0)
                
            finally:
                await self.async_tearDown()
        
        # 非同期テストを実行
        asyncio.run(run_test())
