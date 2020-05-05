from django.urls import re_path

from . import views

app_name = 'speedy.match.matches'
urlpatterns = [
    re_path(route=r'^$', view=views.MatchesListView.as_view(), name='list'),
    re_path(route=r'^settings/$', view=views.MatchSettingsDefaultRedirectView.as_view(), name='settings'),
    re_path(route=r'^settings/about-my-match/$', view=views.EditMatchSettingsView.as_view(), name='edit_match_settings'),
    re_path(route=r'^settings/about-me/$', view=views.EditAboutMeView.as_view(), name='edit_about_me'),
]


