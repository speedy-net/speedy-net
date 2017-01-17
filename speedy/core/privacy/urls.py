from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
]
