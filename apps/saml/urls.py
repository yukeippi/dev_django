from django.urls import path
from . import views

app_name = 'saml'

urlpatterns = [
    path('login/', views.saml_login, name='login'),
    path('acs/', views.saml_acs, name='acs'),
    path('sls/', views.saml_sls, name='sls'),
    path('metadata/', views.saml_metadata, name='metadata'),
]
