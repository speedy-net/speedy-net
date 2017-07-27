from django.conf.urls import url
from . import views

from speedy.core.accounts.urls import urlpatterns
from speedy.core.accounts.views import EditProfileNotificationsView as CoreEditProfileNotificationsView

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^edit-profile/notifications/$', CoreEditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns
