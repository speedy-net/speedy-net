from django.urls import re_path

from . import views

app_name = 'speedy.core.privacy'
urlpatterns = [
    re_path(route=r'', view=views.PrivacyPolicyView.as_view(), name='privacy_policy'),
]


