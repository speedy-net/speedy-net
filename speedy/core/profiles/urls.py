from django.conf.urls import url

from . import views

app_name = 'speedy.core.profiles'
urlpatterns = [
    url(regex=r'^me/(?P<rest>.*)?$', view=views.MeView.as_view(), name='me'),
    url(regex=r'^(?P<slug>[-\._\w]+)/$', view=views.UserDetailView.as_view(), name='user'),
]


