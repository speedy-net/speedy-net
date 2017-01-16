from django.conf.urls import url

from . import views
from speedy.core.accounts_core.urls import urlpatterns

urlpatterns += [
    url(r'^edit-profile/privacy/$', views.EditProfilePrivacyView.as_view(), name='edit_profile_privacy')
]
