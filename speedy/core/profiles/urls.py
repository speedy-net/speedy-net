from django.urls import path, re_path

from . import views

app_name = 'speedy.core.profiles'
urlpatterns = [
    re_path(route=r'^me/(?P<rest>.*)?$', view=views.MeView.as_view(), name='me'),
    path(route='<slug:slug>/', view=views.UserDetailView.as_view(), name='user'),
]


