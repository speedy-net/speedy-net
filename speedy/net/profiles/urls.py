from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^me/(?P<rest>.*)?$', views.MeView.as_view(), name='me'),
    url(r'^(?P<slug>[-\w]+)/$', views.UserDetailView.as_view(), name='user'),
]
