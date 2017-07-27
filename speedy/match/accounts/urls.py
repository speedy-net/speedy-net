from django.conf.urls import url

from . import views
from speedy.core.accounts.urls import urlpatterns

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^edit-profile/privacy/$', views.EditProfilePrivacyView.as_view(), name='edit_profile_privacy'),
] + urlpatterns
