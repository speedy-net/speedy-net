from django.urls import re_path

from . import views
from speedy.core.accounts.urls import urlpatterns

app_name = 'speedy.match.accounts'
urlpatterns = [
    re_path(route=r'^$', view=views.IndexView.as_view(), name='index'),
    re_path(route=r'^welcome/$', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    re_path(route=r'^registration-step-(?P<step>[0-9]+)/$', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    re_path(route=r'^edit-profile/notifications/$', view=views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns


