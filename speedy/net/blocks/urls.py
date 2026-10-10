"""
URL configuration for the Speedy Net blocks app. Adds the blocked users list view on top of the shared core blocks URL patterns.
"""
from django.urls import path

from . import views
from speedy.core.blocks.urls import urlpatterns

app_name = 'speedy.net.blocks'
urlpatterns = [
    path(route='blocked-users/', view=views.BlockedUsersListView.as_view(), name='blocked_users_list'),
] + urlpatterns


