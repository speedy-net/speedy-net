from django.urls import path

from . import views

app_name = 'speedy.core.privacy'
urlpatterns = [
    path(route='', view=views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path(route='<path:rest>', view=views.PrivacyPolicyView.as_view(), name='privacy_policy'),
]


