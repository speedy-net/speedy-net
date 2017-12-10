from django.conf.urls import url

from . import views
from speedy.core.accounts.urls import urlpatterns

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^welcome/$', views.ActivateSiteProfileView.as_view(), name='welcome'),
    url(r'^registration-step-(?P<step>[0-9]+)/$', views.ActivateSiteProfileView.as_view(), name='activate'),
    url(r'^edit-profile/notifications/$', views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns
