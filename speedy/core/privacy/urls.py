from django.conf.urls import url

from . import views

app_name = 'speedy.core.privacy'
urlpatterns = [
    url(r'', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
]


