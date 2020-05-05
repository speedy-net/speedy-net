from django.urls import re_path
from . import views

from speedy.core.accounts.urls import urlpatterns
from speedy.core.accounts import views as core_views

app_name = 'speedy.net.accounts'
urlpatterns = [
    re_path(route=r'^$', view=views.IndexView.as_view(), name='index'),
    re_path(route=r'^welcome/$', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    re_path(route=r'^edit-profile/notifications/$', view=core_views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns


