from django.conf.urls import url
from . import views

from speedy.core.accounts.urls import urlpatterns
from speedy.core.accounts import views as core_views

app_name = 'speedy.net.accounts'
urlpatterns = [
    url(regex=r'^$', view=views.IndexView.as_view(), name='index'),
    url(regex=r'^welcome/$', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    url(regex=r'^edit-profile/notifications/$', view=core_views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns


