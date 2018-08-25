from django.conf.urls import url

from . import views

app_name = 'speedy.core.profiles'
urlpatterns = [
    url(r'^me/(?P<rest>.*)?$', views.MeView.as_view(), name='me'),
    url(r'^(?P<slug>[-\._\w]+)/$', views.UserDetailView.as_view(), name='user'),
]


