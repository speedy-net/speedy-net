from django.conf.urls import url
from . import views

from speedy.core.accounts.urls import urlpatterns
from speedy.core.accounts import views as core_views

app_name = 'speedy.net.accounts'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^welcome/$', core_views.ActivateSiteProfileView.as_view(), name='activate'),
    url(r'^edit-profile/notifications/$', core_views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns


