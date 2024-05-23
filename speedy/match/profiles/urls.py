from django.urls import path, re_path

from . import views

app_name = 'speedy.match.profiles'
urlpatterns = [
    re_path(route=r'^me/(?P<rest>.*)?$', view=views.speedy_core_profiles_views.MeView.as_view(), name='me'),
    path(route='<speedy_slug:slug>/', view=views.UserDetailView.as_view(), name='user'),
]


