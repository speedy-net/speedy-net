from django.conf.urls import url

from . import views

app_name = 'speedy.core.blocks'
urlpatterns = [
    url(regex=r'^blocked-users/$', view=views.BlockedUsersListView.as_view(), name='blocked_users_list'),
    url(regex=r'^block/$', view=views.BlockView.as_view(), name='block'),
    url(regex=r'^unblock/$', view=views.UnblockView.as_view(), name='unblock'),
]


