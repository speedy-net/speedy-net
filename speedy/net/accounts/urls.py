from django.urls import path
from . import views

from speedy.core.accounts.urls import urlpatterns
from speedy.core.accounts import views as core_views

app_name = 'speedy.net.accounts'
urlpatterns = [
    path(route='', view=views.IndexView.as_view(), name='index'),
    path(route='welcome/', view=views.ActivateSiteProfileView.as_view(), name='activate'),
    path(route='edit-profile/notifications/', view=core_views.EditProfileNotificationsView.as_view(), name='edit_profile_notifications'),
] + urlpatterns


