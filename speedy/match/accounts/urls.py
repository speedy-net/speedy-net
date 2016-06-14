from django.conf.urls import url

from . import views
from speedy.net.accounts.urls import urlpatterns

urlpatterns.insert(0, url(r'^edit-profile/$', views.EditProfileView.as_view(), name='edit_profile'))
