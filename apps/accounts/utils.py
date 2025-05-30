"""
SAML認証用のユーティリティ関数
"""
from typing import Any, Dict, Optional
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


def create_saml_user(created: bool, **kwargs: Any) -> User:
    """
    SAML認証でユーザーが作成された際のカスタム処理
    
    Args:
        created (bool): ユーザーが新規作成されたかどうか
        **kwargs: SAML属性から取得した情報
    
    Returns:
        User: 作成または更新されたユーザーオブジェクト
    """
    user: Optional[User] = kwargs.get('user')
    attributes: Dict[str, Any] = kwargs.get('attributes', {})
    
    if user is None:
        raise ValueError("User object is required in kwargs")
    
    if created:
        logger.info(f"新しいSAMLユーザーが作成されました: {user.username}")
        
        # 追加の属性設定
        if 'department' in attributes:
            # カスタムプロファイルがある場合の例
            # user.profile.department = attributes['department'][0]
            # user.profile.save()
            pass
        
        # 特定のグループに追加
        # from django.contrib.auth.models import Group
        # default_group = Group.objects.get(name='SAML Users')
        # user.groups.add(default_group)
        
    else:
        logger.info(f"既存のSAMLユーザーがログインしました: {user.username}")
        
        # 既存ユーザーの属性更新
        updated = False
        
        if 'email' in attributes and attributes['email']:
            new_email = attributes['email'][0]
            if user.email != new_email:
                user.email = new_email
                updated = True
        
        if 'first_name' in attributes and attributes['first_name']:
            new_first_name = attributes['first_name'][0]
            if user.first_name != new_first_name:
                user.first_name = new_first_name
                updated = True
        
        if 'last_name' in attributes and attributes['last_name']:
            new_last_name = attributes['last_name'][0]
            if user.last_name != new_last_name:
                user.last_name = new_last_name
                updated = True
        
        if updated:
            user.save()
            logger.info(f"ユーザー情報を更新しました: {user.username}")
    
    return user
