"""
SAML認証ビュー (シンプル実装)
"""
import os
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages


def saml_login(request):
    """SAML認証開始（デモ用）"""
    # 実際のSAML認証の代わりに、デモ用のメッセージを表示
    messages.info(request, 'SAML認証が設定されました。実際のIdPと連携するには、IdPのメタデータとSP証明書を設定してください。')
    return redirect('accounts:login')


@csrf_exempt
@require_http_methods(["POST"])
def saml_acs(request):
    """SAML Assertion Consumer Service（デモ用）"""
    # 実際のSAML応答処理の代わりに、デモ用の処理
    return render(request, 'saml/demo.html', {
        'message': 'SAML ACS エンドポイントが呼び出されました。実際の実装では、ここでSAML応答を処理します。'
    })


def saml_sls(request):
    """SAML Single Logout Service（デモ用）"""
    return redirect(settings.SAML_LOGOUT_REDIRECT_URL)


def saml_metadata(request):
    """SAMLメタデータを返す（デモ用）"""
    metadata = '''<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="http://localhost:8000/saml/metadata/">
    <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true"
                        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                     Location="http://localhost:8000/saml/acs/" index="1"/>
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                                Location="http://localhost:8000/saml/sls/"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>'''
    
    return HttpResponse(content=metadata, content_type='text/xml')
