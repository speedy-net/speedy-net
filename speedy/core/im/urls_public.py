from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^compose/$', views.SendMessageToUserView.as_view(), name='user_send'),
]
