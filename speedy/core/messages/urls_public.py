from django.urls import re_path

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    re_path(route=r'^compose/$', view=views.SendMessageToUserView.as_view(), name='user_send'),
]


