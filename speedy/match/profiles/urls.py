from django.urls import re_path

from . import views

app_name = 'speedy.match.profiles'
urlpatterns = [
    re_path(route=r'^me/(?P<rest>.*)?$', view=views.MeView.as_view(), name='me'),
    re_path(route=r'^(?P<slug>[-\._\w]+)/$', view=views.UserDetailView.as_view(), name='user'),
]


