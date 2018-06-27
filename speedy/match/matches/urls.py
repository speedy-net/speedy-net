from django.conf.urls import url

from . import views

app_name = 'speedy.match.matches'
urlpatterns = [
    url('^$', views.MatchesListView.as_view(), name='list'),
    url('^settings/$', views.EditMatchSettingsView.as_view(), name='edit_settings'),
    url('^settings/about-me/$', views.EditAboutMeView.as_view(), name='edit_about_me'),
]
