from django.urls import path

from . import views
from speedy.core.blocks.urls import urlpatterns

app_name = 'speedy.net.blocks'
urlpatterns = [
    path(route='blocked-users/', view=views.BlockedUsersListView.as_view(), name='blocked_users_list'),
] + urlpatterns


