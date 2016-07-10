from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.BlockListView.as_view(), name='list'),
    url(r'^block/$', views.BlockView.as_view(), name='block'),
    url(r'^unblock/$', views.UnblockView.as_view(), name='unblock'),
]
