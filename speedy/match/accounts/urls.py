from django.conf.urls import url

from . import views
from speedy.core.accounts.urls import urlpatterns

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^edit-profile/notifications/$', views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns
