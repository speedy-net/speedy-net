from django.urls import path

from . import views

app_name = 'speedy.match.matches'
urlpatterns = [
    path(route='', view=views.MatchesListView.as_view(), name='list'),
    path(route='settings/', view=views.MatchSettingsDefaultRedirectView.as_view(), name='settings'),
    path(route='settings/about-my-match/', view=views.EditMatchSettingsView.as_view(), name='edit_match_settings'),
    path(route='settings/about-me/', view=views.EditAboutMeView.as_view(), name='edit_about_me'),
]


