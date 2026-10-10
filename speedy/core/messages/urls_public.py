"""
URL configuration for the public messages pages (sending a message to a user) of the messages app of Speedy Core.
"""
from django.urls import path

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    path(route='compose/', view=views.SendMessageToUserView.as_view(), name='user_send'),
]


