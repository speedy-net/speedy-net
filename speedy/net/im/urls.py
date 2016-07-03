from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='list'),
]
