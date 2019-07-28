from django.conf.urls import url

from . import views
from speedy.core.accounts.urls import urlpatterns

app_name = 'speedy.match.accounts'
urlpatterns = [
    url(regex=r'^$', view=views.IndexView.as_view(), name='index'),
    url(regex=r'^welcome/$', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    url(regex=r'^registration-step-(?P<step>[0-9]+)/$', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    url(regex=r'^edit-profile/notifications/$', view=views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns


