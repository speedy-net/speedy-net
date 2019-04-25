from django.conf.urls import url

from . import views

app_name = 'speedy.match.matches'
urlpatterns = [
    url(regex=r'^$', view=views.MatchesListView.as_view(), name='list'),
    url(regex=r'^settings/$', view=views.EditMatchSettingsView.as_view(), name='edit_settings'),
    url(regex=r'^settings/about-me/$', view=views.EditAboutMeView.as_view(), name='edit_about_me'),
]


