from django.urls import re_path

from . import views

app_name = 'speedy.core.blocks'
urlpatterns = [
    re_path(route=r'^blocked-users/$', view=views.BlockedUsersListView.as_view(), name='blocked_users_list'),
    re_path(route=r'^block/$', view=views.BlockView.as_view(), name='block'),
    re_path(route=r'^unblock/$', view=views.UnblockView.as_view(), name='unblock'),
]


